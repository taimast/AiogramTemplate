from aiogram import F

from .actions import AdminAction, Action
from .mixins import ActionMixin


class AdminCallback(ActionMixin, prefix="admin"):
    id: int | None = None
    action: Action | AdminAction
    data: str | None = None

    @classmethod
    def stats(cls):
        return cls(action=AdminAction.STATS)

    @classmethod
    def filter_stats(cls):
        return cls.filter(F.action == AdminAction.STATS)

    @classmethod
    def mailing(cls):
        return cls(action=AdminAction.MAILING)

    @classmethod
    def filter_mailing(cls):
        return cls.filter(F.action == AdminAction.MAILING)

    @classmethod
    def export_users(cls):
        return cls(action=AdminAction.EXPORT_USERS)

    @classmethod
    def filter_export_users(cls):
        return cls.filter(F.action == AdminAction.EXPORT_USERS)

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
