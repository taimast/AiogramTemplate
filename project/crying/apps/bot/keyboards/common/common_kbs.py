from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

from aiogram.filters.callback_data import CallbackData
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardButton, KeyboardButton, InlineKeyboardMarkup
from aiogram.utils import markdown as md
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

IKB = InlineKeyboardButton
KB = KeyboardButton
md = md
if TYPE_CHECKING:
    from .....locales.stubs.ru.stub import TranslatorRunner


def subscribe_channel(channels: Iterable[int | str], l10n: TranslatorRunner):
    builder = InlineKeyboardBuilder()
    for channel in channels:
        if "https://t.me/" not in channel:
            channel = f"https://t.me/{channel}"

        builder.button(text=l10n.channel.button.subscribe(), url=channel)
    builder.adjust(1)
    builder.row(IKB(text=l10n.channel.button.subscribed(), callback_data="start"))
    return builder.as_markup()


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
