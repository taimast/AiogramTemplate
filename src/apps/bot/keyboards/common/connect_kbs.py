from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from ...callback_data.connect import ConnectCallback, ConnectAction

if TYPE_CHECKING:
    from .....locales.stubs.ru.stub import TranslatorRunner


def connect(user_id: int, l10n: TranslatorRunner) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    # Принять и Отклонить
    builder.button(
        text=l10n.conversation.connect.button.accept(),
        callback_data=ConnectCallback(user_id=user_id, action=ConnectAction.CONNECT))
    # builder.button(
    #     text=l10n.conversation.connect.button.reject(),
    #     callback_data=ConnectCallback(user_id=user_id, action=ConnectAction.CONNECT)
    # )
    return builder.as_markup()


def is_done() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="✔️ Завершено",
        callback_data="is_done"
    )
    return builder.as_markup()


def disconnect(l10n: TranslatorRunner) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text=l10n.conversation.button.end())
    return builder.as_markup(resize_keyboard=True)
