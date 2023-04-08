from enum import Enum

from aiogram.filters.callback_data import CallbackData


class Action(str, Enum):
    all = "all"
    view = "view"
    create = "create"
    delete = "delete"
    edit = "edit"
    connect = "connect"

    done = "done"
    return_order = "return_order"


class UserCallback(CallbackData, prefix="user"):
    id: int
    action: Action


class ConnectCallback(CallbackData, prefix="connect"):
    action: Action
    force: bool = False
    user_id: int | None


class OrderCallback(CallbackData, prefix="order"):
    user_id: int
    action: Action
