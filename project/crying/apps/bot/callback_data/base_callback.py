from enum import Enum
from typing import Optional

from aiogram.filters.callback_data import CallbackData


class Action(str, Enum):
    all = "all"
    view = "view"
    create = "create"
    delete = "delete"
    edit = "edit"


class UserCallback(CallbackData, prefix="user"):
    pk: int
    action: Action


class ChannelCallback(CallbackData, prefix="channel"):
    pk: Optional[int]
    action: str
