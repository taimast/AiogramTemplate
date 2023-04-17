from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram.filters.callback_data import CallbackData
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton
from aiogram.utils import markdown as md
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

md = md
if TYPE_CHECKING:
    from .....locales.stubs.ru.stub import TranslatorRunner


def start() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="Start", callback_data="start")
    return builder.as_markup(resize_keyboard=True)


def custom_back(callback_data: str | CallbackData = "start") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="« Назад", callback_data=callback_data)
    return builder.as_markup()


def inline_button(text: str, callback_date: CallbackData) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text=text,
        callback_data=callback_date.pack()
    )


def custom_back_button(text: str = "« Назад", callback_data: str | CallbackData = "start", ) -> InlineKeyboardButton:
    if not isinstance(callback_data, str):
        callback_data = callback_data.pack()
    return InlineKeyboardButton(text=text, callback_data=callback_data)


def reply_back_button(l10n: TranslatorRunner) -> KeyboardButton:
    return KeyboardButton(text=l10n.button.back())


def reply_back() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="« Назад")
    return builder.as_markup(resize_keyboard=True)
