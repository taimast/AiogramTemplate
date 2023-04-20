from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

if TYPE_CHECKING:
    from ...locales.stubs.ru.stub import TranslatorRunner


def connect(link: str, l10n: TranslatorRunner) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    # builder.button(
    #     text=l10n.conversation.moderator.button.connect(),
    #     callback_data=ConnectCallback(user_id=user_id, action=Action.connect)
    # )
    builder.button(
        # text=l10n.conversation.moderator.button.connect(),
        text=l10n.order.manager.button.take(),
        url=link
    )
    return builder.as_markup()


def disconnect(l10n: TranslatorRunner) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text=l10n.conversation.button.end())
    return builder.as_markup(resize_keyboard=True)
