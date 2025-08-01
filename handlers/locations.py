from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from config import config
from handlers.httpx_client import client
from handlers.other import cancel_handler
from states.locations import LocationStates

router = Router()

@router.message(F.text.lower() == "локации")
async def locations(message: Message):
    kb = [
        [KeyboardButton(text="Все локации")],
        [KeyboardButton(text="Добавить локацию")],
        [KeyboardButton(text="Удалить локацию")],
        [KeyboardButton(text="Главное меню")]
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выбери действие"
    )

    await message.answer("Какое действие тебя интересует?", reply_markup=keyboard)


@router.message(F.text.lower() == "все локации")
async def all_locations(message: Message):
    data = {'user': message.from_user.id}
    response = await client.get(f'{config.API_URL}/locations/', params=data)
    response_data = response.json()
    if not response_data:
        await message.answer("Список локаций пуст")
    else:
        response_text = [x['loc_name'] for x in response.json()]
        await message.answer("Список всех локаций:" + "\n" + "\n".join(f"{x + 1}. {name}" for x, name in enumerate(response_text)))


@router.message(F.text.lower() == "добавить локацию")
async def add_name_of_loc(message: Message, state: FSMContext):
    await state.set_state(LocationStates.wait_add_name)
    kb = [
        [KeyboardButton(text="Отмена")]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)
    await message.answer("Введи название локации", reply_markup=keyboard)


@router.message(LocationStates.wait_add_name)
async def add_address_of_loc(message:Message, state: FSMContext):
    if message.text == 'Отмена':
        await cancel_handler(message)
        await state.clear()
    else:
        await state.update_data(loc_name=message.text)
        await state.set_state(LocationStates.wait_add_address)
        kb = [
            [KeyboardButton(text="Отмена")]
        ]
        keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)
        await message.answer("Введи адрес локации", reply_markup=keyboard)


@router.message(LocationStates.wait_add_address)
async def add_location(message: Message, state: FSMContext):
    if message.text == 'Отмена':
        await cancel_handler(message)
        await state.clear()
    else:
        await state.update_data(address=message.text)
        data_1 = {'user': message.from_user.id}
        data_2 = await state.get_data()
        data = data_2 | data_1
        response = await client.post(f'{config.API_URL}/locations/', data=data)
        await message.answer(response.text.strip('"'))
        await state.clear()


@router.message(F.text.lower() == "удалить локацию")
async def del_loc(message: Message, state: FSMContext):
    await state.set_state(LocationStates.wait_del)
    await message.answer("Введи название локации, которую хочешь удалить")


@router.message(LocationStates.wait_del)
async def del_location(message:Message, state: FSMContext):
    data = {'user': message.from_user.id, 'loc_name': message.text}
    response = await client.delete(f'{config.API_URL}/location/', params=data)
    await message.answer(response.text.strip('"'))
    await state.clear()