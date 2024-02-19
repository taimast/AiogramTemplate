from __future__ import annotations

from aiogram.filters.callback_data import CallbackData
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram.utils import markdown as md
from aiogram.utils.keyboard import (
    ReplyKeyboardBuilder as _ReplyKeyboardBuilder,
    InlineKeyboardBuilder as _InlineKeyboardBuilder
)

IKB = InlineKeyboardButton
KB = KeyboardButton
md = md


class CustomInlineKeyboardBuilder(_InlineKeyboardBuilder):

    def add_back(self, text: str = "«", cd: str | CallbackData = "start") -> InlineKeyboardMarkup:
        if not isinstance(cd, str):
            cd = cd.pack()
        self.row(IKB(text=text, callback_data=cd))
        return self.as_markup()

    def add_admin_back(self, text: str = "«", cd: str | CallbackData = "admin") -> InlineKeyboardMarkup:
        return self.add_back(text, cd)

    def add_start_back(self, text: str = "«", cd: str | CallbackData = "start") -> InlineKeyboardMarkup:
        return self.add_back(text, cd)


class CustomReplyKeyboardBuilder(_ReplyKeyboardBuilder):

    def add_back(self, text: str = "«") -> ReplyKeyboardMarkup:
        self.row(KB(text=text))
        return self.as_markup(resize_keyboard=True)


def custom_back_kb(text: str = "«", cd: str | CallbackData = "start") -> InlineKeyboardMarkup:
    builder = CustomInlineKeyboardBuilder()
    builder.button(text=text, callback_data=cd)
    return builder.as_markup()


def custom_reply_kb(text: str = "«") -> ReplyKeyboardMarkup:
    builder = CustomReplyKeyboardBuilder()
    builder.button(text=text)
    return builder.as_markup(resize_keyboard=True)


def reply_back() -> ReplyKeyboardMarkup:
    return custom_reply_kb()
