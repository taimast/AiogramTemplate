from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


# todo 5/31/2022 2:33 PM taima: разделить основно функционал
def admin_start():
    keywords = [
        # "mailing"
        ("📨 Рассылка", "mailing"),
        ("📊 Статистика", "stats"),
    ]
    builder = InlineKeyboardBuilder()

    for text, callback_data in keywords:
        builder.button(text=text, callback_data=callback_data)

    builder.adjust(1)
    return builder.as_markup()
    # return get_inline_keyboard(keyword)


def admin_button() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Админ панель", callback_data="admin")
    return builder.as_markup()


def back() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="« Назад", callback_data="admin")
    return builder.as_markup()
