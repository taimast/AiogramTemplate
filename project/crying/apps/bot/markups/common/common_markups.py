from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from project.crying.apps.bot.middleware.language import _
from project.crying.db.models import Channel


def start() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="Start", callback_data="start")
    return builder.as_markup(resize_keyboard=True)


def is_subscribed_to_channel(channels: list[Channel]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for num, channel in enumerate(channels, 1):
        builder.button(text=_("Канал #{}").format(num), url=f"https://t.me/{channel.username}")
    builder.button(text=_("✅ Я подписался"), callback_data="check_subscribe")
    builder.adjust(1)
    return builder.as_markup()


def check_subscribe() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text='start', callback_data="start")
    return builder.as_markup()
