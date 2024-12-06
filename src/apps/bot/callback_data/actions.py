from enum import StrEnum

from fluentogram import TranslatorRunner


class Action(StrEnum):
    GET = "get"
    CREATE = "create"
    DELETE = "delete"
    UPDATE = "update"
    ALL = "all"
    MENU = "menu"


class ConnectAction(StrEnum):
    CONNECT = "connect"
    DISCONNECT = "disconnect"


class AdminAction(StrEnum):
    STATS = "stats"
    MAILING = "mailing"
    EXPORT_USERS = "export_users"
    RETRACT_LAST_MAILING = "retract_last_mailing"
    MAILING_CANCEL = "mailing_cancel"
    EDIT_TEXTS = "edit_texts"
    EDIT_TEXT = "edit_text"
    ADMINS = "admins"
    STATS_MENU = "stats_menu"


class ModeratorAction(StrEnum):
    SWITCH = "switch"


class UserAction(StrEnum):
    REFERRALS = "referrals"
    # Добавить информацию
    ADD_INFO = "add_info"
    # Удалить информацию
    DELETE_INFO = "delete_info"

    def get_text(self, l10n: TranslatorRunner):
        return l10n.get(f"admin-user-action-{self}")
