from aiogram.filters.callback_data import CallbackData
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from project.crying.apps.bot.locales.stub.ru.stub import TranslatorRunner


def start() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="Start", callback_data="start")
    return builder.as_markup(resize_keyboard=True)


def custom_back(callback_data: str | CallbackData = "start") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="« Назад", callback_data=callback_data)
    return builder.as_markup()


def custom_back_button(l10n: TranslatorRunner, callback_data: str | CallbackData = "start", ) -> InlineKeyboardButton:
    if not isinstance(callback_data, str):
        callback_data = callback_data.pack()
    return InlineKeyboardButton(text=l10n.button.back(), callback_data=callback_data)


def reply_back() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="« Назад")
    return builder.as_markup(resize_keyboard=True)
