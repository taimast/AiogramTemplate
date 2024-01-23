from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def start() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="Start", callback_data="start")
    return builder.as_markup(resize_keyboard=True)


def inline_start() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Start", callback_data="start")
    builder.button(text="WEB", web_app=WebAppInfo(url="https://5609-81-163-58-130.ngrok-free.app"))

    return builder.as_markup(resize_keyboard=True)
