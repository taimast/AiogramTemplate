import asyncio
from typing import TypeVar

from aiogram import types
from aiogram.exceptions import TelegramBadRequest
from bs4 import BeautifulSoup
from loguru import logger

MESSAGE_LIMIT = 4096
ReplyMarkup = TypeVar(
    "ReplyMarkup",
    types.InlineKeyboardMarkup,
    types.ReplyKeyboardMarkup,
    types.ReplyKeyboardRemove,
    types.ForceReply,
)

SUPPORTED_TAGS_SIGN = ["b", "i", "a", "code", "pre"]


async def split_sending(
    message: types.Message,
    answer_text: str,
    reply_markup: ReplyMarkup | None = None,
):
    """Split message if it's length is more than 4096 symbols"""
    answer_length = len(answer_text)
    if answer_length > MESSAGE_LIMIT:
        for _from in range(0, answer_length, MESSAGE_LIMIT):
            _to = _from + MESSAGE_LIMIT
            if _to >= answer_length:
                await message.answer(answer_text[_from:_to], reply_markup=reply_markup)
            else:
                await message.answer(answer_text[_from:_to])
            await asyncio.sleep(0.5)
    else:
        await message.answer(answer_text, reply_markup=reply_markup)


async def split_sending_proper(
    message: types.Message,
    answer_text: str,
    reply_markup: ReplyMarkup | None = None,
):
    """
    Split message if it's length is more than 4096 symbols
       and remove all tags except supported and replace them with children
    """
    answer_length = len(answer_text)
    if answer_length > MESSAGE_LIMIT:
        for _from in range(0, answer_length, MESSAGE_LIMIT):
            _to = _from + MESSAGE_LIMIT
            text = answer_text[_from:_to]
            soup = BeautifulSoup(text, "lxml")
            # remove all tags except supported
            for tag in soup.find_all():
                if tag.name not in SUPPORTED_TAGS_SIGN:
                    tag.replaceWithChildren()
            text = str(soup)
            try:
                if _to >= answer_length:
                    await message.answer(text, reply_markup=reply_markup)
                else:
                    await message.answer(text, reply_markup=reply_markup)
            except TelegramBadRequest as e:
                logger.warning(f"TelegramBadRequest: {e}")
                raise
            await asyncio.sleep(0.5)
    else:
        await message.answer(answer_text, reply_markup=reply_markup)


def parse_buttons(text: str) -> list[list[dict[str, str]]]:
    """
    🔄 Отправьте мне список URL-кнопок в одном сообщении. Пожалуйста, следуйте этому формату:

    Кнопка 1 - http://example1.com
    Кнопка 2 - http://example2.com


    Используйте разделитель |, чтобы добавить до трех кнопок в один ряд. Пример:

    Кнопка 1 - http://example1.com | Кнопка 2 - http://example2.com
    Кнопка 3 - http://example3.com | Кнопка 4 - http://example4.com



    Нажмите кнопку «Отмена», чтобы вернуться к добавлению сообщений.
    Или введите «skip»
    """

    if not text.strip():
        return []

    rows_of_buttons = []
    for row in text.split("\n"):
        button_row = []
        for button in row.split("|"):
            try:
                button_text, button_url = button.split("-", 1)
                button_row.append({"text": button_text.strip(), "url": button_url.strip()})
            except ValueError:
                # Handle cases where split is not possible or wrong format
                continue

        if button_row:
            rows_of_buttons.append(button_row)

    return rows_of_buttons
