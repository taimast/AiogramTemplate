from __future__ import annotations

from enum import StrEnum
from typing import Sequence, Callable, Any, TypeVar, Self

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

    def make(self, offset: int) -> Self:
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

    def has_next(self, length: int, page: int = 0) -> bool:
        return self.offset + self.limit < length - page

    def has_prev(self, page: int = 0) -> bool:
        return self.offset > page

    def slice(self, items: Sequence[T]) -> Sequence[T]:
        return items[self.offset:self.offset + self.limit]

    def sort(self, items: list[T], key: Callable[[T], Any]) -> list[T]:
        if not self.sort_order:
            return items
        return sorted(items, key=key, reverse=self.sort_order == SortOrder.DESC)

    def add_pagination_buttons(self, builder: InlineKeyboardBuilder, length: int):
        has5prev_cd = self.switch_to(self.offset - 4 * self.limit).pack() if self.has_prev(
            4) else self.switch_to_first().pack()
        has5next_cd = self.switch_to(self.offset + 6 * self.limit).pack() if self.has_next(
            length, 5) else self.switch_to_last(length).pack()
        has1prev_cd = self.prev().pack() if self.has_prev() else self.switch_to_last(length).pack()
        has1next_cd = self.next().pack() if self.has_next(length) else self.switch_to_first().pack()
        builder.row(
            # В самое начало
            IKButton(text="≺≺", callback_data=self.switch_to_first().pack()),
            # Назад на 5 страниц
            IKButton(text="≺5", callback_data=has5prev_cd),
            # Назад на 1 страницу
            IKButton(text="≺", callback_data=has1prev_cd),
            # Вперед на 1 страницу
            IKButton(text="≻", callback_data=has1next_cd),
            # по 5 страниц вперед
            IKButton(text="≻5", callback_data=has5next_cd),
            # В самый конец
            IKButton(text="≻≻", callback_data=self.switch_to_last(length).pack())
        )
        counter_str = f"{self.offset // self.limit + 1}/{(length - 1) // self.limit + 1}"
        builder.row(IKButton(text=counter_str, callback_data="None"))

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
