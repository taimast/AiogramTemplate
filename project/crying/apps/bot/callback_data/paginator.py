from __future__ import annotations

from enum import StrEnum
from typing import Self, Sequence, Callable, Any, TypeVar

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton as IKButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

T = TypeVar("T")


class SortOrder(StrEnum):
    ASC = "asc"
    DESC = "desc"


class PaginatorCallback(CallbackData, prefix="paginator"):
    offset: int = 0
    limit: int = 10
    sort_order: SortOrder | None = None

    def make(self, offset: int):
        return PaginatorCallback(
            offset=offset,
            limit=self.limit,
            sort_order=self.sort_order
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

    def slice(self, items: Sequence[T]) -> Sequence[T]:
        return items[self.offset:self.offset + self.limit]

    def sort(self, items: list[T], key: Callable[[T], Any]) -> list[T]:
        if not self.sort_order:
            return items
        return sorted(items, key=key, reverse=self.sort_order == SortOrder.DESC)

    def add_pagination_buttons(self, builder: InlineKeyboardBuilder, length: int):
        builder.row(
            # В самое начало
            IKButton(
                text="≺≺",
                callback_data=self.switch_to_first().pack()
            ),

            IKButton(
                text="≺",
                # if not has prev set last page
                callback_data=self.prev().pack() if self.has_prev() else self.switch_to_last(length).pack()
            ),
            IKButton(
                text=f"{self.offset // self.limit + 1}/{(length - 1) // self.limit + 1}",
                callback_data="None"
            ),
            IKButton(
                text="≻",
                callback_data=self.next().pack() if self.has_next(length) else self.switch_to_first().pack()
            ),
            # В самый конец
            IKButton(
                text="≻≻",
                callback_data=self.switch_to_last(length).pack()
            )
        )

    # Кнопки сортировки по убыванию и возрастанию
    def add_sort_buttons(self, builder: InlineKeyboardBuilder):
        asc_callback = self.make(self.offset)
        asc_callback.sort_order = SortOrder.ASC
        default_callback = self.make(self.offset)
        default_callback.sort_order = None
        desc_callback = self.make(self.offset)
        desc_callback.sort_order = SortOrder.DESC
        builder.row(
            IKButton(
                text="🔺",
                callback_data=asc_callback.pack()
            ),
            IKButton(
                text="🌟",
                callback_data=default_callback.pack()
            ),
            IKButton(
                text="🔻",
                callback_data=desc_callback.pack()
            )
        )
