from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def statistics_start() -> InlineKeyboardMarkup:
    keywords = [
        ("👥 Узнать количество пользователей.", "users_count"),
        ("👥 Количество новых пользователей за сегодня.", "users_count_new"),
        # ("👥 Количество пользователей онлайн.", "users_count_online"),
    ]
    builder = InlineKeyboardBuilder()
    for keyword, payload in keywords:
        builder.button(text=keyword, callback_data=payload)

    return builder.as_markup()


def back() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅ Назад", callback_data="statistics")
    return builder.as_markup()
