from aiogram.filters.callback_data import CallbackData

from .base import Action


class AdminCallback(CallbackData, prefix="admin"):
    id: int | None = None
    action: Action
