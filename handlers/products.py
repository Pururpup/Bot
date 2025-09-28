from datetime import datetime
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from httpx_client import client
from states.products import ProductStates
from config import config
from other import cancel_handler

router = Router()

@router.message(F.text.lower() == "товары")
async def products(message: Message):
    kb = [
        [KeyboardButton(text="Информация о товаре")],
        [KeyboardButton(text="Все товары")],
        [KeyboardButton(text="Добавить товар")],
        [KeyboardButton(text="Удалить товар")],
        [KeyboardButton(text="Главное меню")]
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выбери действие"
    )

    await message.answer("Какое действие тебя интересует?", reply_markup=keyboard)


@router.message(F.text.lower() == "информация о товаре")
async def find_prod(message: Message, state: FSMContext):
    await state.set_state(ProductStates.wait_find_prod)
    await message.answer("Введи название товара")


@router.message(ProductStates.wait_find_prod)
async def find_product(message: Message, state: FSMContext):
    data = {'product_name': message.text, 'user': message.from_user.id}
    response = await client.get(f'{config.API_URL}/product/', params=data)
    if not response.json():
        await message.answer("Товар не найден")

    response_text = "\n".join([
        f"Название товара: {response.json()['product_name']}",
        f"Дата поступления: {response.json()['receipt_date']}",
        f"Стоимость покупки: {response.json()['purchase_price']}",
        f"Дата продажи: {response.json()['sale_date']}",
        f"Стоимость продажи: {response.json()['sale_price']}",
        f"Стоимость ремонта: {response.json()['repair_price']}",
        f"Количество на складе: {response.json()['quantity_in_stock']}",
        f"Количество в доставке: {response.json()['quantity_in_delivery']}",
        f"Категория: {response.json()['category_name']}",
        f"Место покупки: {response.json()['location_of_purchase_name']}",
        f"Место продажи: {response.json()['location_of_sale_name']}"
    ])
    await message.answer(response_text)
    await state.clear()


@router.message(F.text.lower() == "все товары")
async def all_products(message: Message):
    data = {'user': message.from_user.id}
    response = await client.get(f'{config.API_URL}/products/', params=data)
    response_data = response.json()
    if not response_data:
        await message.answer("Список товаров пуст")
    else:
        response_text = [x['product_name'] for x in response.json()]
        await message.answer(
            "Список всех товаров:" + "\n" + "\n".join(f"{x + 1}. {name}" for x, name in enumerate(response_text)))


@router.message(F.text.lower() == "добавить товар")
async def add_prod(message: Message, state: FSMContext):
    await state.set_state(ProductStates.wait_add_name)
    kb = [
        [KeyboardButton(text="Отмена")]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)
    await message.answer("Введи название товара", reply_markup=keyboard)


@router.message(ProductStates.wait_add_name)
async def add_product_name(message: Message, state: FSMContext):
    if message.text == 'Отмена':
        await cancel_handler(message)
        await state.clear()
    else:
        await state.update_data(product_name=message.text)
        await state.set_state(ProductStates.wait_add_receipt_date)
        kb = [
            [KeyboardButton(text="Отмена")]
        ]
        keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)
        await message.answer("Введи дату поступления товара на склад в формате: дд.мм.гггг", reply_markup=keyboard)


@router.message(ProductStates.wait_add_receipt_date)
async def add_receipt_date(message: Message, state: FSMContext):
    if message.text == 'Отмена':
        await cancel_handler(message)
        await state.clear()
    else:
        try:
            await state.update_data(receipt_date=datetime.strptime(message.text, "%d.%m.%Y").date())
            await state.set_state(ProductStates.wait_add_purchase_price)
            kb = [
                [KeyboardButton(text="Отмена")]
            ]
            keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)
            await message.answer("Введи стоимость покупки товара (только число)", reply_markup=keyboard)
        except ValueError:
            await message.answer("Неверный формат даты, используйте: дд.мм.гггг")


@router.message(ProductStates.wait_add_purchase_price)
async def add_purchase_price(message: Message, state: FSMContext):
    if message.text == 'Отмена':
        await cancel_handler(message)
        await state.clear()
    else:
        try:
            price = float(message.text.replace(",", "."))
            if price < 0 or price > 99_999_999.99:
                await message.answer("Стоимость выходит из допустимого диапазона, введи корректную стоимость")
            else:
                await state.update_data(purchase_price=round(price, 2))
                await state.set_state(ProductStates.wait_add_sale_date)
                kb = [
                    [KeyboardButton(text="Пропустить")],
                    [KeyboardButton(text="Отмена")]
                ]
                keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)
                await message.answer("Введи дату продажи товара (если она есть) в формате: дд.мм.гггг", reply_markup=keyboard)
        except ValueError:
            await message.answer("Введи корректную стоимость")


@router.message(ProductStates.wait_add_sale_date)
async def add_sale_date(message: Message, state: FSMContext):
    if message.text == 'Отмена':
        await cancel_handler(message)
        await state.clear()
    else:
        try:
            if message.text == "Пропустить":
                await state.update_data(sale_date=None)
            else:
                await state.update_data(sale_date=datetime.strptime(message.text, "%d.%m.%Y").date())
            await state.set_state(ProductStates.wait_add_sale_price)
            kb = [
                [KeyboardButton(text="Пропустить")],
                [KeyboardButton(text="Отмена")]
            ]
            keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)
            await message.answer("Введи стоимость продажи (только число)", reply_markup=keyboard)
        except ValueError:
            await message.answer("Неверный формат даты, используйте: дд.мм.гггг")


@router.message(ProductStates.wait_add_sale_price)
async def add_sale_price(message: Message, state: FSMContext):
    if message.text == 'Отмена':
        await cancel_handler(message)
        await state.clear()
    else:
        try:
            if message.text == "Пропустить":
                await state.update_data(sale_price=None)
            else:
                price = float(message.text.replace(",", "."))
                if price < 0 or price > 99_999_999.99:
                    await message.answer("Стоимость выходит из допустимого диапазона, введи корректную стоимость")
                    return
                await state.update_data(sale_price=round(price, 2))
            await state.set_state(ProductStates.wait_add_repair_price)
            kb = [
                [KeyboardButton(text="Пропустить")],
                [KeyboardButton(text="Отмена")]
            ]
            keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)
            await message.answer("Введи стоимость ремонта", reply_markup=keyboard)
        except ValueError:
            await message.answer("Введи корректную стоимость")


@router.message(ProductStates.wait_add_repair_price)
async def add_repair_price(message: Message, state: FSMContext):
    if message.text == 'Отмена':
        await cancel_handler(message)
        await state.clear()
    else:
        try:
            if message.text == "Пропустить":
                await state.update_data(repair_price=None)
            else:
                price = float(message.text.replace(",", "."))
                if price < 0 or price > 99_999_999.99:
                    await message.answer("Стоимость выходит из допустимого диапазона, введи корректную стоимость")
                    return
                await state.update_data(repair_price=round(price, 2))
            await state.set_state(ProductStates.wait_add_quantity_in_stock)
            kb = [
                [KeyboardButton(text="Отмена")]
            ]
            keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)
            await message.answer("Введи количество товара на складе", reply_markup=keyboard)
        except ValueError:
            await message.answer("Введи корректную стоимость")


@router.message(ProductStates.wait_add_quantity_in_stock)
async def add_quantity_in_stock(message: Message, state: FSMContext):
    if message.text == 'Отмена':
        await cancel_handler(message)
        await state.clear()
    else:
        try:
            quantity = int(message.text)
            if quantity < 0:
                await message.answer("Количество не может быть отрицательным, введи корректное число")
            else:
                await state.update_data(quantity_in_stock=quantity)
                await state.set_state(ProductStates.wait_add_quantity_in_delivery)
                kb = [
                    [KeyboardButton(text="Отмена")]
                ]
                keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)
                await message.answer("Введи количество товара в доставке", reply_markup=keyboard)
        except ValueError:
            await message.answer("Введи корректное число")


@router.message(ProductStates.wait_add_quantity_in_delivery)
async def add_quantity_in_delivery(message: Message, state: FSMContext):
    if message.text == 'Отмена':
        await cancel_handler(message)
        await state.clear()
    else:
        try:
            quantity = int(message.text)
            if quantity < 0:
                await message.answer("Количество не может быть отрицательным, введи корректное число")
            else:
                await state.update_data(quantity_in_delivery=quantity)

                await state.set_state(ProductStates.wait_choose_category)
                data = {'user': message.from_user.id}
                response = await client.get(f'{config.API_URL}/categories/', params=data)
                if response.status_code == 200:
                    categories = response.json()
                    kb = [
                            [KeyboardButton(text=category["cat_name"])] for category in categories
                        ] + [
                            [KeyboardButton(text="Отмена")]
                        ]

                    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)
                    await message.answer("Выбери категорию, которой принадлежит товар", reply_markup=keyboard)
        except ValueError:
            await message.answer("Введи корректное число")


@router.message(ProductStates.wait_choose_category)
async def add_category(message: Message, state: FSMContext):
    if message.text == 'Отмена':
        await cancel_handler(message)
        await state.clear()
    else:
        data = {'user': message.from_user.id, 'cat_name': message.text}
        response = await client.get(f'{config.API_URL}/category/', params=data)
        await state.update_data(category=response.json()['id'])

        await state.set_state(ProductStates.wait_choose_loc_of_purchase)
        data = {'user': message.from_user.id}
        response = await client.get(f'{config.API_URL}/locations/', params=data)
        if response.status_code == 200:
            locations_of_purchase = response.json()
            kb = [
                    [KeyboardButton(text=location["loc_name"])] for location in locations_of_purchase
                ] + [
                    [KeyboardButton(text="Отмена")]
                ]
            keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)
            await message.answer("Выбери место покупки товара", reply_markup=keyboard)


@router.message(ProductStates.wait_choose_loc_of_purchase)
async def add_loc_of_purchase(message: Message, state: FSMContext):
    if message.text == 'Отмена':
        await cancel_handler(message)
        await state.clear()
    else:
        data = {'user': message.from_user.id, 'loc_name': message.text}
        response = await client.get(f'{config.API_URL}/location/', params=data)
        await state.update_data(location_of_purchase=response.json()['id'])

        await state.set_state(ProductStates.wait_choose_loc_of_sale)
        data = {'user': message.from_user.id}
        response = await client.get(f'{config.API_URL}/locations/', params=data)
        if response.status_code == 200:
            locations_of_sale = response.json()
            kb = [
                    [KeyboardButton(text=location["loc_name"])] for location in locations_of_sale
                ] + [
                    [KeyboardButton(text="Отмена")]
                ]
            keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)
            await message.answer("Выбери место продажи товара", reply_markup=keyboard)


@router.message(ProductStates.wait_choose_loc_of_sale)
async def add_loc_of_sale(message: Message, state: FSMContext):
    if message.text == 'Отмена':
        await cancel_handler(message)
        await state.clear()
    else:
        data = {'user': message.from_user.id, 'loc_name': message.text}
        response = await client.get(f'{config.API_URL}/location/', params=data)
        await state.update_data(location_of_sale=response.json()['id'])

        await state.set_state(ProductStates.wait_save_product)
        kb = [
            [KeyboardButton(text="Сохранить товар")],
            [KeyboardButton(text="Отмена")]
        ]
        keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)
        await message.answer("Нажмите, если хотите сохранить товар",reply_markup=keyboard)


@router.message(ProductStates.wait_save_product)
async def save_product(message: Message, state: FSMContext):
    if message.text == 'Отмена':
        await cancel_handler(message)
        await state.clear()
    else:
        data_1 = {'user': message.from_user.id}
        data_2 = await state.get_data()
        data = data_2 | data_1
        response = await client.post(f'{config.API_URL}/products/', data=data)
        kb = [
            [KeyboardButton(text="Главное меню")]
        ]
        keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)
        await message.answer(response.text.strip('"'), reply_markup=keyboard)
        await state.clear()


@router.message(F.text.lower() == "удалить товар")
async def del_prod(message: Message, state: FSMContext):
    await state.set_state(ProductStates.wait_del_prod)
    await message.answer("Введи название товара, который хочешь удалить")


@router.message(ProductStates.wait_del_prod)
async def del_product(message: Message, state: FSMContext):
    data = {'user': message.from_user.id, 'product_name': message.text}
    response = await client.delete(f'{config.API_URL}/product/', params=data)
    await message.answer(response.text.strip('"'))
    await state.clear()

