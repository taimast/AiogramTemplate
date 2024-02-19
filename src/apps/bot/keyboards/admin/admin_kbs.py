from aiogram.types import InlineKeyboardMarkup

from src.apps.bot.callback_data.actions import Action
from src.apps.bot.callback_data.admin import AdminCallback
from src.apps.bot.keyboards.common.helper_kbs import CustomInlineKeyboardBuilder


# todo 5/31/2022 2:33 PM taima: разделить основно функционал
def admin_start():
    builder = CustomInlineKeyboardBuilder()
    builder.button(text="📨 Рассылка", callback_data=AdminCallback.mailing())
    # Отозвать последнюю рассылку
    builder.button(text="🔄 Отозвать последнюю рассылку", callback_data=AdminCallback.retract_last_mailing())
    builder.button(text="📊 Статистика", callback_data=AdminCallback.stats())
    builder.button(text="📥 Выгрузка пользователей", callback_data=AdminCallback.export_users())
    builder.button(text="👤 Админы", callback_data=AdminCallback(action=Action.ALL))

    builder.adjust(1)
    return builder.as_markup()


def mailing_cancel():
    builder = CustomInlineKeyboardBuilder()
    builder.button(text="🔴 Отменить", callback_data="mailing_cancel")
    return builder.as_markup()


def admins(admins: list[int]) -> InlineKeyboardMarkup:
    builder = CustomInlineKeyboardBuilder()
    for admin in admins:
        builder.button(text=str(admin), callback_data=AdminCallback(action=Action.DELETE, id=admin))
    builder.button(text="Добавить админа", callback_data=AdminCallback(action=Action.CREATE))
    builder.adjust(1)
    builder.add_admin_back()
    return builder.as_markup()


def admin_button() -> InlineKeyboardMarkup:
    builder = CustomInlineKeyboardBuilder()
    builder.add_admin_back("Админ панель")
    return builder.as_markup()


def back() -> InlineKeyboardMarkup:
    builder = CustomInlineKeyboardBuilder()
    builder.add_admin_back()
    return builder.as_markup()
