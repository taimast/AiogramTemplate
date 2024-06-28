from typing import Self

from aiogram import F
from aiogram.filters.callback_data import CallbackData

from .actions import Action


class FilterActionMixin(CallbackData, prefix="filter_action_mixin"):
    action: Action

    @classmethod
    def filter_create(cls) -> Self:
        return cls.filter(F.action == Action.CREATE)

    @classmethod
    def filter_all(cls) -> Self:
        return cls.filter(F.action == Action.ALL)

    @classmethod
    def filter_delete(cls) -> Self:
        return cls.filter(F.action == Action.DELETE)

    @classmethod
    def filter_get(cls) -> Self:
        return cls.filter(F.action == Action.GET)


class ActionCreateMixin(CallbackData, prefix="action_copy_mixin"):
    action: Action

    def get(self, id: int) -> Self:
        return self.model_copy(update={'action': Action.GET, 'id': id})

    def all(self) -> Self:
        return self.model_copy(update={'action': Action.ALL})

    def create(self) -> Self:
        return self.model_copy(update={'action': Action.CREATE})

    def delete(self) -> Self:
        return self.model_copy(update={'action': Action.DELETE})

    @classmethod
    def new_create(cls) -> Self:
        return cls(action=Action.CREATE)

    @classmethod
    def new_get(cls, id: int) -> Self:
        return cls(action=Action.GET, id=id)

    @classmethod
    def new_delete(cls, id: int) -> Self:
        return cls(action=Action.DELETE, id=id)

    @classmethod
    def new_all(cls) -> Self:
        return cls(action=Action.ALL)


# Общий класс для миксинов
class ActionMixin(ActionCreateMixin, FilterActionMixin, CallbackData, prefix="action_mixin"):
    pass
