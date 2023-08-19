from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram.filters.callback_data import CallbackData
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton
from aiogram.utils import markdown as md
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

IKB = InlineKeyboardButton
KB = KeyboardButton
md = md
if TYPE_CHECKING:
    from .....locales.stubs.ru.stub import TranslatorRunner


def start() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="Start", callback_data="start")
    return builder.as_markup(resize_keyboard=True)


def inline_start() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Start", callback_data="start")

    return builder.as_markup(resize_keyboard=True)


def custom_back(callback_data: str | CallbackData = "start") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="« Назад", callback_data=callback_data)
    return builder.as_markup()


def custom_back_kb(text: str = "« Назад", cd: str | CallbackData = "start") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=text, callback_data=cd)
    return builder.as_markup()


def inline_button(text: str, cd: CallbackData) -> InlineKeyboardButton:
    return IKB(text=text, callback_data=cd.pack())


def custom_back_inline_button(text: str = "« Назад", cd: str | CallbackData = "start") -> InlineKeyboardButton:
    if not isinstance(cd, str):
        cd = cd.pack()
    return IKB(text=text, callback_data=cd)


def custom_reply_kb(text: str = "« Назад") -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text=text)
    return builder.as_markup(resize_keyboard=True)


def reply_back_button(l10n: TranslatorRunner) -> KeyboardButton:
    return KeyboardButton(text=l10n.button.back())


def reply_back() -> ReplyKeyboardMarkup:
    return custom_reply_kb()
