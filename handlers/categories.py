from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from handlers.httpx_client import client
from states.categories import CategoryStates
from config import config
from handlers.other import cancel_handler
router = Router()


@router.message(F.text.lower() == "категории")
async def categories(message: Message):
    kb = [
        [KeyboardButton(text="Все категории")],
        [KeyboardButton(text="Добавить категорию")],
        [KeyboardButton(text="Удалить категорию")],
        [KeyboardButton(text="Главное меню")]
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выбери действие"
    )

    await message.answer("Какое действие тебя интересует?", reply_markup=keyboard)


@router.message(F.text.lower() == "все категории")
async def all_categories(message: Message):
    data = {'user': message.from_user.id}
    response = await client.get(f'{config.API_URL}/categories/', params=data)
    response_data = response.json()
    if not response_data:
        await message.answer("Список категорий пуст")
    else:
        response_text = [x['cat_name'] for x in response.json()]
        await message.answer("Список всех категорий:" + "\n" + "\n".join(f"{x + 1}. {name}" for x, name in enumerate(response_text)))


@router.message(F.text.lower() == "добавить категорию")
async def add_cat(message: Message, state: FSMContext):
    await state.set_state(CategoryStates.wait_add)
    kb = [
        [KeyboardButton(text="Отмена")]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)
    await message.answer("Введи название категории", reply_markup=keyboard)


@router.message(CategoryStates.wait_add)
async def add_category(message:Message, state: FSMContext):
    if message.text == 'Отмена':
        await cancel_handler(message)
    else:
        data = {'cat_name': message.text, 'user': message.from_user.id}
        response = await client.post(f'{config.API_URL}/categories/', data=data)
        await message.answer(response.text.strip('"'))
    await state.clear()


@router.message(F.text.lower() == "удалить категорию")
async def del_cat(message: Message, state: FSMContext):
    await state.set_state(CategoryStates.wait_del)
    await message.answer("Введи название категории, которую хочешь удалить")


@router.message(CategoryStates.wait_del)
async def del_category(message:Message, state: FSMContext):
    data = {'user': message.from_user.id, 'cat_name': message.text}
    response = await client.delete(f'{config.API_URL}/category/', params=data)
    await message.answer(response.text.strip('"'))
    await state.clear()

