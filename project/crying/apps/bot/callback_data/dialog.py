from enum import Enum

from aiogram.filters.callback_data import CallbackData


class PagiAction(str, Enum):
    prev = "prev"
    next = "next"


class PaginationCallback(CallbackData, prefix="pagination"):
    action: PagiAction
    offset: int
