from enum import StrEnum
from typing import Self, TypeVar

from aiogram.filters.callback_data import CallbackData

T = TypeVar("T")


class PaginatorAction(StrEnum):
    prev = "prev"
    next = "next"


class PaginatorCallback(CallbackData, prefix="paginator"):
    action: PaginatorAction = PaginatorAction.next
    offset: int = 0
    limit: int = 10

    def next(self) -> Self:
        return PaginatorCallback(
            action=PaginatorAction.next,
            offset=self.offset + self.limit,
            limit=self.limit
        )

    def prev(self) -> Self:
        return PaginatorCallback(
            action=PaginatorAction.prev,
            offset=self.offset - self.limit,
            limit=self.limit
        )

    def has_next(self, length: int) -> bool:
        return self.offset + self.limit < length

    def has_prev(self) -> bool:
        return self.offset > 0

    def slice(self, items: list[T]) -> list[T]:
        return items[self.offset:self.offset + self.limit]
