from __future__ import annotations

from enum import StrEnum
from typing import Any, Callable, Self, Sequence

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton as IKButton
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.apps.bot.keyboards.common.helper_kbs import CustomInlineKeyboardBuilder

DEFAULT_LIMIT = 10

SEGMENT_SIZE = 3
BIG_JUMP_SEGMENT_SIZE = 2

PAGE_BACK_SYMBOL = "‹"
PAGE_FORWARD_SYMBOL = "›"
PAGE_BIG_BACK_SYMBOL = "«"
PAGE_BIG_FORWARD_SYMBOL = "»"

ASC_SORT_SYMBOL = "▲"
DESC_SORT_SYMBOL = "▼"


class SortOrder(StrEnum):
    ASC = "asc"
    DESC = "desc"


class PaginatorCallback[T](CallbackData, prefix="paginator"):
    offset: int = 0
    limit: int = DEFAULT_LIMIT
    sort_order: SortOrder | None = None
    data: str | None = None

    def make(self, offset: int) -> Self:
        return self.model_copy(update={"offset": offset, "sort_order": None})

    def make_btn(self, text: str, offset: int) -> IKButton:
        return IKButton(text=text, callback_data=self.make(offset).pack())

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
        return items[self.offset : self.offset + self.limit]

    def slice_first(self, items: Sequence[T]) -> T:
        return self.slice(items)[0]

    def can_paginate(self, length: int) -> bool:
        return length > self.limit

    def sort(
        self,
        items: Sequence[T],
        key: Callable[[T], Any],
    ) -> Sequence[T]:
        if not self.sort_order:
            return items
        return sorted(
            items,
            key=key,
            reverse=self.sort_order == SortOrder.DESC,
        )

    def current_page(self, length: int) -> int:
        return self.offset // self.limit

    def add_base_pagination_buttons(
        self,
        builder: InlineKeyboardBuilder,
        length: int,
    ):
        if not self.can_paginate(length):
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
            IKButton(text=PAGE_BIG_BACK_SYMBOL, callback_data=self.switch_to_first().pack()),
            # Назад на 5 страниц
            IKButton(text=f"{PAGE_BACK_SYMBOL} 5", callback_data=has5prev_cd.pack()),
            # Назад на 1 страницу
            IKButton(text=PAGE_BACK_SYMBOL, callback_data=has1prev_cd.pack()),
            # Вперед на 1 страницу
            IKButton(text=PAGE_FORWARD_SYMBOL, callback_data=has1next_cd.pack()),
            # по 5 страниц вперед
            IKButton(text=f"5{PAGE_FORWARD_SYMBOL}", callback_data=has5next_cd.pack()),
            # В самый конец
            IKButton(
                text=PAGE_BIG_FORWARD_SYMBOL, callback_data=self.switch_to_last(length).pack()
            ),
        )
        first_page = self.offset // self.limit
        last_page = length // self.limit
        counter_str = f"{first_page} / {last_page}"
        builder.row(IKButton(text=counter_str, callback_data="None"))

    def add_minimal_pagination_buttons(
        self,
        builder: CustomInlineKeyboardBuilder,
        length: int,
    ):
        if not self.can_paginate(length):
            return
        current_page = self.current_page(length)

        current_segment = current_page // SEGMENT_SIZE
        min_range = current_segment * SEGMENT_SIZE
        max_page = length // self.limit
        max_range = min(min_range + SEGMENT_SIZE, max_page)

        rows = []
        if current_segment > BIG_JUMP_SEGMENT_SIZE:
            prev_range = min_range // BIG_JUMP_SEGMENT_SIZE
            rows.append(
                self.make_btn(
                    f"{PAGE_BIG_BACK_SYMBOL} {prev_range}",
                    prev_range * self.limit,
                )
            )

        if current_segment > 0:
            prev_range = min_range - 1
            rows.append(
                self.make_btn(
                    f"{PAGE_BACK_SYMBOL} {prev_range}",
                    prev_range * self.limit,
                )
            )
        for i in range(min_range, max_range):
            text = str(i)
            if i == current_page:
                text = f"· {text} ·"
            offset = i * self.limit
            rows.append(self.make_btn(text, offset))

        if max_range < max_page:
            rows.append(
                self.make_btn(
                    f"{max_range} {PAGE_FORWARD_SYMBOL}",
                    max_range * self.limit,
                )
            )

            x3_segment = max_range * BIG_JUMP_SEGMENT_SIZE
            x3_segment = min(x3_segment, max_page)
            if x3_segment <= max_page:
                rows.append(
                    self.make_btn(
                        f"{x3_segment} {PAGE_BIG_FORWARD_SYMBOL}",
                        x3_segment * self.limit,
                    )
                )

        builder.row(*rows)

    # Кнопки сортировки по убыванию и возрастанию
    def add_sort_buttons(self, builder: InlineKeyboardBuilder):
        asc_callback = self.make(self.offset)
        asc_callback.sort_order = SortOrder.ASC
        default_callback = self.make(self.offset)
        default_callback.sort_order = None
        desc_callback = self.make(self.offset)
        desc_callback.sort_order = SortOrder.DESC
        builder.row(
            IKButton(text="▲", callback_data=asc_callback.pack()),
            # IKButton(text="🌟", callback_data=default_callback.pack()),
            IKButton(text="▼", callback_data=desc_callback.pack()),
        )

    def get_keyboard(self, length: int = 0) -> InlineKeyboardMarkup:
        builder = CustomInlineKeyboardBuilder()
        self.add_minimal_pagination_buttons(builder, length)
        self.add_sort_buttons(builder)
        return builder.as_markup()
