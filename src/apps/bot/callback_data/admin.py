from aiogram import F

from src.apps.bot.callback_data.moderator import ModeratorPermission

from .actions import Action, AdminAction
from .mixins import ActionMixin


class AdminCallback(ActionMixin, prefix="admin"):
    id: int | None = None
    action: Action | AdminAction | ModeratorPermission
    data: str | None = None

    @classmethod
    def start_menu(cls):
        return cls(action=AdminAction.STATS_MENU)

    @classmethod
    def filter_stats_menu(cls):
        return cls.filter(F.action == AdminAction.STATS_MENU)

    @classmethod
    def stats(cls):
        return cls(action=AdminAction.STATS)

    @classmethod
    def filter_stats(cls):
        return cls.filter(F.action == AdminAction.STATS)

    @classmethod
    def common_stats(cls):
        return cls(action=ModeratorPermission.STATS)

    @classmethod
    def filter_common_stats(cls):
        return cls.filter(F.action == ModeratorPermission.STATS)

    @classmethod
    def mailing(cls):
        return cls(action=AdminAction.MAILING)

    @classmethod
    def filter_mailing(cls):
        return cls.filter((F.action == AdminAction.MAILING) & (F.data == None))

    @classmethod
    def start_mailing(cls):
        return cls(action=AdminAction.MAILING, data="start")

    @classmethod
    def filter_start_mailing(cls):
        return cls.filter((F.action == AdminAction.MAILING) & (F.data == "start"))

    @classmethod
    def export_users(cls):
        return cls(action=AdminAction.EXPORT_USERS)

    @classmethod
    def filter_export_users(cls):
        return cls.filter(F.action == AdminAction.EXPORT_USERS)

    @classmethod
    def filter_user_stats(cls):
        return cls.filter(F.action == ModeratorPermission.USER_STATS)

    @classmethod
    def retract_last_mailing(cls):
        return cls(action=AdminAction.RETRACT_LAST_MAILING)

    @classmethod
    def filter_retract_last_mailing(cls):
        return cls.filter(F.action == AdminAction.RETRACT_LAST_MAILING)

    @classmethod
    def mailing_cancel(cls):
        return cls(action=AdminAction.MAILING_CANCEL)

    @classmethod
    def filter_mailing_cancel(cls):
        return cls.filter(F.action == AdminAction.MAILING_CANCEL)
