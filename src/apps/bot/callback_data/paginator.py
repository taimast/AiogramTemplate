from __future__ import annotations

from enum import StrEnum
from typing import Sequence, Callable, Any, TypeVar, Self

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton as IKButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

T = TypeVar("T")


class SortOrder(StrEnum):
    ASC = "asc"
    DESC = "desc"


class PaginatorCallback(CallbackData, prefix="paginator"):
    offset: int = 0
    limit: int = 10
    sort_order: SortOrder | None = None
    data: str | None = None

    def make(self, offset: int) -> Self:
        return self.model_copy(update={"offset": offset})

    def next(self) -> Self:
        return self.make(self.offset + self.limit)

    def prev(self) -> Self:
        return self.make(self.offset - self.limit)

    def switch_to(self, page: int) -> Self:
        """
         Switch to page.
         Fist page is 0
        :param page:
        :return:
        """
        return self.make(page * self.limit)

    def switch_to_last(self, length: int) -> Self:
        last_page = length // self.limit
        if length % self.limit == 0:
            last_page -= 1
        return self.switch_to(last_page)

    def switch_to_first(self) -> Self:
        return self.switch_to(0)

    def has_prev(self, page: int = 0) -> bool:
        return self.offset > page * self.limit

    def has_next(self, length: int, page: int = 0) -> bool:
        return self.offset + self.limit < length - page * self.limit

    def slice(self, items: Sequence[T]) -> Sequence[T]:
        return items[self.offset:self.offset + self.limit]

    def slice_first(self, items: Sequence[T]) -> T:
        return self.slice(items)[0]

    def sort(self, items: list[T], key: Callable[[T], Any]) -> list[T]:
        if not self.sort_order:
            return items
        return sorted(items, key=key, reverse=self.sort_order == SortOrder.DESC)

    def add_pagination_buttons(self, builder: InlineKeyboardBuilder, length: int):
        if length <= self.limit:
            return
        prev5offset = self.offset - 5 * self.limit
        has5prev = self.has_prev(5)
        has5prev_cd = self.make(prev5offset) if has5prev else self.switch_to_first()

        next5offset = self.offset + 5 * self.limit
        has5next = self.has_next(length, 5)
        has5next_cd = self.make(next5offset) if has5next else self.switch_to_last(length)

        has1prev_cd = self.prev() if self.has_prev() else self.switch_to_last(length)
        has1next_cd = self.next() if self.has_next(length) else self.switch_to_first()
        builder.row(
            # В самое начало
            IKButton(text="≪", callback_data=self.switch_to_first().pack()),
            # Назад на 5 страниц
            IKButton(text="≺5", callback_data=has5prev_cd.pack()),
            # Назад на 1 страницу
            IKButton(text="≺", callback_data=has1prev_cd.pack()),
            # Вперед на 1 страницу
            IKButton(text="≻", callback_data=has1next_cd.pack()),
            # по 5 страниц вперед
            IKButton(text="5≻", callback_data=has5next_cd.pack()),
            # В самый конец
            IKButton(text="≫", callback_data=self.switch_to_last(length).pack())
        )
        first_page = self.offset // self.limit
        last_page = length // self.limit
        counter_str = f"{first_page} / {last_page}"
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

    def get_keyboard(self, length: int = 0) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        self.add_pagination_buttons(builder, length)
        self.add_sort_buttons(builder)
        return builder.as_markup()
