from enum import IntEnum, auto, StrEnum


class Action(IntEnum):
    GET = auto()
    CREATE = auto()
    DELETE = auto()
    UPDATE = auto()
    ALL = auto()
    MENU = auto()


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
