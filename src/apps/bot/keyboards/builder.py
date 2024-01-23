from dataclasses import dataclass, field
from typing import TypeVar, Self

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardMarkup, ReplyKeyboardMarkup

MarkupType = TypeVar("MarkupType", InlineKeyboardMarkup, ReplyKeyboardMarkup)


@dataclass
class Dialog:
    markups: list[MarkupType] = field(default_factory=list)

    @classmethod
    def create(cls, with_markup: MarkupType) -> Self:
        return cls([with_markup])

    @classmethod
    def add_back(cls, markup: MarkupType, ) -> Self:
        markup.inline_keyboard[-1].append(
            InlineKeyboardButton(text="«", callback_data="dialog_back")
        )
        return cls.create(markup)

    def add(self, markup: MarkupType) -> MarkupType:
        self.add_back(markup)
        self.markups.append(markup)
        return markup

    def back(self) -> MarkupType:
        return self.markups.pop()
