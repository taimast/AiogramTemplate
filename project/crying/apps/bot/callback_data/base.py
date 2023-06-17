from enum import StrEnum

from aiogram.filters.callback_data import CallbackData


class Action(StrEnum):
    GET = "get"
    CREATE = "create"
    DELETE = "delete"
    UPDATE = "update"
    ALL = "all"
    MENU = "menu"


class UserCallback(CallbackData, prefix="user"):
    id: int
    action: Action
