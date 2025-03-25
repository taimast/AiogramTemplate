from typing import Iterable

from aiogram.types import InlineKeyboardMarkup
from fluentogram import TranslatorRunner

from src.apps.bot.callback_data.actions import (
    Action,
    AdminAction,
    ModeratorAction,
    UserAction,
)
from src.apps.bot.callback_data.admin import AdminCallback
from src.apps.bot.callback_data.moderator import ModeratorCallback, ModeratorPermission
from src.apps.bot.callback_data.user import UserCallback
from src.apps.bot.keyboards.common.helper_kbs import CustomInlineKeyboardBuilder
from src.config import Settings
from src.config.moderator import Moderator
from src.config.settings import BotSettings
from src.db.models.user.user import Locale

PERMS = (ModeratorPermission.MAILING,)

STATS_PERMS = (
    ModeratorPermission.STATS,
    ModeratorPermission.EXPORT_USERS,
    ModeratorPermission.USER_STATS,
)

EXTRA_PERMS = ()


def admin_start(user_id: int, stts: BotSettings, l10n: TranslatorRunner):
    builder = CustomInlineKeyboardBuilder()
    builder.button(
        text=l10n.get("admin-stats-button-menu"),
        callback_data=AdminCallback(action=AdminAction.STATS_MENU),
    )

    for perm in PERMS:
        if stts.have_perm(user_id, perm):
            builder.button(
                text=perm.get_text(l10n), callback_data=AdminCallback(action=perm)
            )

    if user_id in stts.admins:
        builder.button(
            text=l10n.get("admin-admins-button-all"),
            callback_data=AdminCallback(action=Action.ALL),
        )
        builder.button(
            text=l10n.get("admin-moderators-button-all"),
            callback_data=ModeratorCallback(action=Action.ALL),
        )
    builder.adjust(2, 2, 2, 2, 1, 2)
    return builder.as_markup()


def stats(user_id: int, stts: BotSettings, l10n: TranslatorRunner):
    builder = CustomInlineKeyboardBuilder()
    for perm in STATS_PERMS:
        if stts.have_perm(user_id, perm):
            builder.button(
                text=perm.get_text(l10n), callback_data=AdminCallback(action=perm)
            )
    builder.adjust(1)
    builder.add_admin_back()
    return builder.as_markup()


def get_moderators(moders: dict[int, Moderator], l10n: TranslatorRunner):
    builder = CustomInlineKeyboardBuilder()
    for moder_id, moder in moders.items():
        builder.button(
            text=f"{moder.id} (@{moder.username})",
            callback_data=ModeratorCallback(action=Action.GET, id=moder.id),
        )
    builder.row_button(
        text=l10n.get("admin-moderator-button-add"),
        callback_data=ModeratorCallback(action=Action.CREATE),
    )
    builder.adjust(1)
    builder.add_admin_back()
    return builder.as_markup()


def get_moderator(moder: Moderator, l10n: TranslatorRunner):
    builder = CustomInlineKeyboardBuilder()
    perm: ModeratorPermission
    for perm in (*PERMS, *STATS_PERMS, *EXTRA_PERMS):
        text = perm.get_text(l10n)
        sign = "🔴"
        if perm in moder.permissions:
            sign = "🟢"
        builder.button(
            text=f"{sign} {text}",
            callback_data=ModeratorCallback(
                id=moder.id, action=ModeratorAction.SWITCH, permission=perm
            ),
        )

    builder.button(
        text=l10n.get("admin-moderator-button-language", locale=moder.locale or "🔴"),
        callback_data=ModeratorCallback(
            id=moder.id,
            action=ModeratorAction.SWITCH,
            permission=ModeratorPermission.LOCALE,
        ),
    )

    builder.adjust(2, 2, 1)
    builder.row_button(
        text=l10n.get("admin-moderator-button-delete"),
        callback_data=ModeratorCallback(id=moder.id, action=Action.DELETE),
    )
    builder.add_admin_back()
    return builder.as_markup()


def confirm_mailing(l10n: TranslatorRunner) -> InlineKeyboardMarkup:
    builder = CustomInlineKeyboardBuilder()
    builder.button(
        text=l10n.get("admin-mailing-button-confirm_yes"),
        callback_data="confirm_mailing",
    )
    builder.add_admin_back()
    return builder.as_markup()


def created_buttons(text: str):
    builder = CustomInlineKeyboardBuilder()
    # Добавьте кнопки для сообщения в формате кнопка1-ссылка1. Каждый с новой строки. Или нажмите Пропустить
    objs = text.split("\n")
    for obj in objs:
        button, url = obj.split("-")
        builder.button(text=button.strip(), url=url.strip())
    builder.one_row()
    return builder.as_markup()


def add_buttons(l10n: TranslatorRunner) -> InlineKeyboardMarkup:
    builder = CustomInlineKeyboardBuilder()
    builder.button(
        text=l10n.get("admin-mailing-button-skip"), callback_data="send_mailing"
    )
    builder.add_admin_back()
    return builder.as_markup()


def mailing_control():
    builder = CustomInlineKeyboardBuilder()
    builder.button(text="🔄 Обновить статистику", callback_data="update_mailing_stats")
    builder.button(text="🔴 Отменить", callback_data="mailing_cancel")
    return builder.as_markup()


def admins(admins: Iterable[int], l10n: TranslatorRunner) -> InlineKeyboardMarkup:
    builder = CustomInlineKeyboardBuilder()
    for admin in admins:
        builder.button(
            text=str(admin), callback_data=AdminCallback(action=Action.DELETE, id=admin)
        )
    builder.button(
        text=l10n.get("admin-admins-button-add"),
        callback_data=AdminCallback(action=Action.CREATE),
    )
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


def edit_texts(sett: Settings):
    builder = CustomInlineKeyboardBuilder()
    for name, field in sett.bot.texts.model_fields.items():
        title = field.title or field.description
        if title:
            builder.button(
                text=title,
                callback_data=AdminCallback(action=AdminAction.EDIT_TEXT, data=name),
            )

    builder.adjust(2)
    builder.add_admin_back()
    return builder.as_markup()


def mailing(l10n: TranslatorRunner):
    builder = CustomInlineKeyboardBuilder()
    builder.button(
        text=l10n.get("admin-mailing-button-start"),
        callback_data=AdminCallback.start_mailing(),
    )
    builder.button(
        text=l10n.get("admin-mailing-button-retract_last"),
        callback_data=AdminCallback.retract_last_mailing(),
    )
    builder.adjust(1)
    builder.add_admin_back()
    return builder.as_markup()


def mailing_language(l10n: TranslatorRunner) -> InlineKeyboardMarkup:
    builder = CustomInlineKeyboardBuilder()
    builder.button(
        text=l10n.get("admin-mailing-button-all"), callback_data="mailing:locale:all"
    )
    builder.button(
        text=l10n.get("admin-mailing-button-private"),
        callback_data="mailing:locale:private",
    )
    for locale in Locale:
        builder.button(
            text=locale.get_text(l10n),
            callback_data=f"mailing:locale:{locale}",
        )
    builder.adjust(2, 1, 2)
    builder.add_admin_back()
    return builder.as_markup(resize_keyboard=True)


def mailing_cancel(l10n: TranslatorRunner):
    builder = CustomInlineKeyboardBuilder()
    builder.button(
        text=l10n.get("admin-mailing-button-cancel"), callback_data="mailing_cancel"
    )
    return builder.as_markup()


def user_stats(user_id: int, l10n: TranslatorRunner):
    builder = CustomInlineKeyboardBuilder()

    for action in UserAction:
        builder.button(
            text=action.get_text(l10n),
            callback_data=UserCallback(id=user_id, action=action),
        )
    builder.adjust(2, 2, 1, 2)
    builder.row_button(
        text=l10n.get("admin-users-button-delete"),
        callback_data=UserCallback(id=user_id, action=Action.DELETE),
    )
    builder.add_back(
        text=l10n.get("button-back_to_prev"),
        cd=AdminCallback(action=ModeratorPermission.USER_STATS),
    )
    builder.add_admin_back(text=l10n.get("button-quit"))
    return builder.as_markup()
