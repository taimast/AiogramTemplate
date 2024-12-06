from aiogram.filters.callback_data import CallbackData

from .actions import Action, UserAction
from .mixins import ActionMixin


# TODO: Убрать None, сделать int по умолчанию
class UserCallback(ActionMixin, CallbackData, prefix="user"):
    id: int | None = None
    action: Action | UserAction
