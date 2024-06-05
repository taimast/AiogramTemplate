import asyncio
from typing import TypeVar

from aiogram import types, Bot
from aiogram.exceptions import TelegramBadRequest
from bs4 import BeautifulSoup
from loguru import logger

MESSAGE_LIMIT = 4096
ReplyMarkup = TypeVar("ReplyMarkup", types.InlineKeyboardMarkup, types.ReplyKeyboardMarkup, types.ReplyKeyboardRemove,
                      types.ForceReply)

SUPPORTED_TAGS_SIGN = ['b', 'i', 'a', 'code', 'pre']


async def split_sending(message: types.Message,
                        answer_text: str,
                        reply_markup: ReplyMarkup = None):
    """ Split message if it's length is more than 4096 symbols """
    answer_length = len(answer_text)
    if answer_length > MESSAGE_LIMIT:
        for _from in range(0, answer_length, MESSAGE_LIMIT):
            _to = _from + MESSAGE_LIMIT
            if _to >= answer_length:
                await message.answer(answer_text[_from: _to], reply_markup=reply_markup)
            else:
                await message.answer(answer_text[_from:_to])
            await asyncio.sleep(0.5)
    else:
        await message.answer(answer_text, reply_markup=reply_markup)


async def mailings(bot: Bot, text: str, users: list | int, *, reply_markup: ReplyMarkup = None) -> list[types.Message]:
    """ Send message to all users in list """
    if isinstance(users, int):
        users = [users]
    mails = []
    for user in users:
        try:
            mails.append(await bot.send_message(user, text, reply_markup=reply_markup))
        except Exception as e:
            print(e)
        await asyncio.sleep(0.5)
    return mails


async def copy_mailings(
        message: types.Message,
        users: list | int, *,
        pre_text: str | None = None,
        after_text: str | None = None,
        reply_markup: ReplyMarkup = None
) -> list[types.Message]:
    """ Send message to all users in list """
    if isinstance(users, int):
        users = [users]
    mails = []
    for user in users:
        try:
            if pre_text:
                await message.bot.send_message(user, pre_text)
            mails.append(
                # await bot.send_message(user, text, reply_markup=reply_markup)
                await message.copy_to(user, reply_markup=reply_markup)
            )
            if after_text:
                await message.bot.send_message(user, after_text)
        except Exception as e:
            print(e)
        await asyncio.sleep(0.5)
    return mails


async def split_sending_proper(message: types.Message,
                               answer_text: str,
                               reply_markup: ReplyMarkup = None):
    """
     Split message if it's length is more than 4096 symbols
        and remove all tags except supported and replace them with children
    """
    answer_length = len(answer_text)
    if answer_length > MESSAGE_LIMIT:
        for _from in range(0, answer_length, MESSAGE_LIMIT):
            _to = _from + MESSAGE_LIMIT
            text = answer_text[_from: _to]
            soup = BeautifulSoup(text, 'lxml')
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
