from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from project.crying.apps.bot.callback_data.admin import AdminCallback
from project.crying.apps.bot.callback_data.base import Action


# todo 5/31/2022 2:33 PM taima: разделить основно функционал
def admin_start():
    keywords = [
        # "mailing"
        ("📨 Рассылка", "mailing"),
        ("📊 Статистика", "stats"),
        # Выгрузка пользователей
        ("📥 Выгрузка пользователей", "export_users"),
        # Админы
        ("👤 Админы", AdminCallback(action=Action.ALL)),
    ]
    builder = InlineKeyboardBuilder()

    for text, callback_data in keywords:
        builder.button(text=text, callback_data=callback_data)

    builder.adjust(1)
    return builder.as_markup()
    # return get_inline_keyboard(keyword)


def admins(admins: list[int]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for admin in admins:
        builder.button(text=str(admin), callback_data=AdminCallback(action=Action.DELETE, id=admin))
    builder.button(text="Добавить админа", callback_data=AdminCallback(action=Action.CREATE))
    builder.adjust(1)
    builder.button(text="« Назад", callback_data="admin")
    return builder.as_markup()


def admin_button() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Админ панель", callback_data="admin")
    return builder.as_markup()


def back() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="« Назад", callback_data="admin")
    return builder.as_markup()
