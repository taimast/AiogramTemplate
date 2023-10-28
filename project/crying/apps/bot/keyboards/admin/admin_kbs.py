from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from project.crying.apps.bot.callback_data.admin import AdminCallback
from project.crying.apps.bot.callback_data.base import Action


# todo 5/31/2022 2:33 PM taima: разделить основно функционал
def admin_start():
    builder = InlineKeyboardBuilder()
    builder.button(text="📨 Рассылка", callback_data="mailing")
    builder.button(text="📊 Статистика", callback_data="stats")
    builder.button(text="📥 Выгрузка пользователей", callback_data="export_users")
    builder.button(text="👤 Админы", callback_data=AdminCallback(action=Action.ALL))

    builder.adjust(1)
    return builder.as_markup()

def mailing_cancel():
    builder = InlineKeyboardBuilder()
    builder.button(text="🔴 Отменить рассылку", callback_data="mailing_cancel")
    return builder.as_markup()


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
