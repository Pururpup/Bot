from aiogram import Router, F
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup

router = Router()

@router.message(F.text.lower() == "фото")
async def photos(message: Message):
    kb = [
        [KeyboardButton(text="Найти фото")],
        [KeyboardButton(text="Все фото")],
        [KeyboardButton(text="Добавить фото")],
        [KeyboardButton(text="Изменить фото")],
        [KeyboardButton(text="Удалить фото")],
        [KeyboardButton(text="Главное меню")]
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выбери действие"
    )

    await message.answer("Какое действие тебя интересует?", reply_markup=keyboard)