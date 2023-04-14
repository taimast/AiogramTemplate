from enum import StrEnum
from typing import Self, TypeVar

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton as IKButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

T = TypeVar("T")


class PaginatorAction(StrEnum):
    prev = "prev"
    next = "next"


class PaginatorCallback(CallbackData, prefix="paginator"):
    offset: int = 0
    limit: int = 10

    def make(self, offset: int):
        return PaginatorCallback(
            offset=offset,
            limit=self.limit
        )

    def next(self) -> Self:
        return self.make(self.offset + self.limit)

    def prev(self) -> Self:
        return self.make(self.offset - self.limit)

    def switch_to(self, page: int) -> Self:
        return self.make((page - 1) * self.limit)

    def switch_to_last(self, length: int) -> Self:
        return self.switch_to((length - 1) // self.limit + 1)

    def switch_to_first(self) -> Self:
        return self.switch_to(1)

    def has_next(self, length: int) -> bool:
        return self.offset + self.limit < length

    def has_prev(self) -> bool:
        return self.offset > 0

    def slice(self, items: list[T]) -> list[T]:
        return items[self.offset:self.offset + self.limit]

    def add_buttons(self, builder: InlineKeyboardBuilder, length: int):
        builder.row(
            IKButton(
                text="«",
                # if not has prev set last page
                callback_data=self.prev().pack() if self.has_prev() else self.switch_to_last(length).pack()
            )
        )
        if self.has_prev() or self.has_next(length):
            builder.button(
                text=f"{self.offset // self.limit + 1}/{(length - 1) // self.limit + 1}",
                callback_data="None"
            )

        builder.button(
            text="»",
            callback_data=self.next() if self.has_next(length) else self.switch_to_first().pack()
        )
