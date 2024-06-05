from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup

from src.apps.bot.keyboards.common.helper_kbs import (
    CustomReplyKeyboardBuilder,
    CustomInlineKeyboardBuilder
)


def start() -> ReplyKeyboardMarkup:
    builder = CustomReplyKeyboardBuilder()
    builder.add_back()
    return builder.as_markup(resize_keyboard=True)


def inline_start() -> InlineKeyboardMarkup:
    builder = CustomInlineKeyboardBuilder()
    builder.button(text="start", url="https://t.me/")
    # builder.add_start_back()
    return builder.as_markup(resize_keyboard=True)
