from enum import IntEnum, auto

from aiogram.filters.callback_data import CallbackData


class Action(IntEnum):
    GET = auto()
    CREATE = auto()
    DELETE = auto()
    UPDATE = auto()
    ALL = auto()
    MENU = auto()


class UserCallback(CallbackData, prefix="user"):
    id: int
    action: Action
