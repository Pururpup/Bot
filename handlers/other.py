from aiogram import F, Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from httpx_client import client
from config import config

router = Router()

@router.message(Command("start"))
async def send_welcome(message: Message):
    user_id = {'user': message.from_user.id}
    user_name = message.from_user.full_name
    user_exists = await client.get(f'{config.API_URL}user/', params=user_id)
    if not user_exists.json().get("is_exists"):
        data = {'telegram_id': message.from_user.id, 'user_name': user_name}
        response = await client.post(f'{config.API_URL}user/', data=data)

    kb = [
        [KeyboardButton(text="Товары")],
        [KeyboardButton(text="Категории")],
        [KeyboardButton(text="Локации")],
        [KeyboardButton(text="Фото")],
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выбери раздел"
    )

    await message.answer("Привет! Это персональный склад. Какой раздел тебя интересует?", reply_markup=keyboard)

@router.message(F.text.lower() == "главное меню")
async def back_to_main_menu(message: Message):
    kb = [
        [KeyboardButton(text="Товары")],
        [KeyboardButton(text="Категории")],
        [KeyboardButton(text="Локации")],
        [KeyboardButton(text="Фото")],
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выбери раздел"
    )

    await message.answer("Вы вернулись в главное меню", reply_markup=keyboard)

@router.message(F.text.lower() == "отмена")
async def cancel_handler(message: Message):
    kb = [
        [KeyboardButton(text="Главное меню")]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)
    await message.answer("Операция отменена", reply_markup=keyboard)