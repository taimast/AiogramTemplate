from __future__ import annotations

from typing import Self

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

    def row_button(self, callback_data: CallbackData | str = None, **kwargs):
        if isinstance(callback_data, CallbackData):
            callback_data = callback_data.pack()
        return self.row(IKB(callback_data=callback_data, **kwargs))

    def add_back(self, text: str = "«", cd: str | CallbackData = "start") -> Self:
        if not isinstance(cd, str):
            cd = cd.pack()
        return self.row(IKB(text=text, callback_data=cd))

    def add_admin_back(self, text: str = "«", cd: str | CallbackData = "admin") -> Self:
        return self.add_back(text, cd)

    def add_start_back(self, text: str = "«", cd: str | CallbackData = "start") -> Self:
        return self.add_back(text, cd)

    def one_row(self):
        return self.adjust(1)


class CustomReplyKeyboardBuilder(_ReplyKeyboardBuilder):

    def add_back(self, text: str = "«") -> Self:
        return self.row(KB(text=text))

    def one_row(self):
        return self.adjust(1)


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
