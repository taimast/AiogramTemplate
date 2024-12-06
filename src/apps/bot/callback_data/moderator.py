from enum import StrEnum

from aiogram.filters.callback_data import CallbackData
from fluentogram import TranslatorRunner

from .actions import Action, ModeratorAction
from .mixins import ActionMixin


class ModeratorPermission(StrEnum):
    MAILING = "mailing"
    STATS = "stats"
    USER_STATS = "user_stats"
    EXPORT_USERS = "export_users"
    LOCALE = "locale"

    def get_text(self, l10n: TranslatorRunner):
        return l10n.get(f"admin-perm-{self}")


class ModeratorCallback(ActionMixin, CallbackData, prefix="moderator"):
    id: int | None = None
    action: Action | ModeratorAction
    permission: ModeratorPermission | None = None
