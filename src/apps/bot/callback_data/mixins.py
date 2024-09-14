from enum import StrEnum
from typing import Self

from aiogram import F
from aiogram.filters.callback_data import CallbackData, CallbackQueryFilter

from .actions import Action


class FilterActionMixin(CallbackData, prefix="filter_action_mixin"):
    action: Action

    @classmethod
    def filter_create(cls) -> CallbackQueryFilter:
        return cls.filter(F.action == Action.CREATE)

    @classmethod
    def filter_all(cls) -> CallbackQueryFilter:
        return cls.filter(F.action == Action.ALL)

    @classmethod
    def filter_delete(cls) -> CallbackQueryFilter:
        return cls.filter(F.action == Action.DELETE)

    @classmethod
    def filter_get(cls) -> CallbackQueryFilter:
        return cls.filter(F.action == Action.GET)

    @classmethod
    def filter_with_action(cls, action: StrEnum) -> CallbackQueryFilter:
        return cls.filter(F.action == action)


class ActionCreateMixin(CallbackData, prefix="action_copy_mixin"):
    action: Action

    def get(self, id: int | None = None) -> Self:
        id = id or self.id
        return self.model_copy(update={"action": Action.GET, "id": id})

    def all(self) -> Self:
        return self.model_copy(update={"action": Action.ALL})

    def create(self) -> Self:
        return self.model_copy(update={"action": Action.CREATE})

    def delete(self) -> Self:
        return self.model_copy(update={"action": Action.DELETE})

    @classmethod
    def new_create(cls, id: int = None) -> Self:
        return cls(action=Action.CREATE, id=id)

    @classmethod
    def new_get(cls, id: int) -> Self:
        return cls(action=Action.GET, id=id)

    @classmethod
    def new_delete(cls, id: int) -> Self:
        return cls(action=Action.DELETE, id=id)

    @classmethod
    def new_all(cls) -> Self:
        return cls(action=Action.ALL)

    @classmethod
    def with_action(cls, action: StrEnum, **kwargs) -> Self:
        return cls(action=action, **kwargs)


# Общий класс для миксинов
class ActionMixin(ActionCreateMixin, FilterActionMixin, CallbackData, prefix="action_mixin"):
    pass
