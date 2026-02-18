from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder



async def register_kb():
    build = InlineKeyboardBuilder()
    build.add(InlineKeyboardButton(text="Зарегистрироваться", callback_data="register_user"))
    return build.as_markup()
