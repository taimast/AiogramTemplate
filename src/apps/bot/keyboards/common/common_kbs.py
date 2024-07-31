from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, WebAppInfo, KeyboardButtonRequestUsers

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
    builder.add_back()
    # builder.add_start_back()
    return builder.as_markup(resize_keyboard=True)
