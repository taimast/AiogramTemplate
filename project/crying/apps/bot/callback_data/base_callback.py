from enum import Enum

from aiogram.filters.callback_data import CallbackData


class Action(str, Enum):
    GET = "get"
    CREATE = "create"
    DELETE = "delete"
    UPDATE = "update"
    ALL = "all"


class UserCallback(CallbackData, prefix="user"):
    id: int
    action: Action
