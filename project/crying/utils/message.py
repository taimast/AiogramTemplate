import asyncio
from typing import TypeVar

from aiogram import types, Bot

MESSAGE_LIMIT = 4096
ReplyMarkup = TypeVar("ReplyMarkup", types.InlineKeyboardMarkup, types.ReplyKeyboardMarkup, types.ReplyKeyboardRemove,
                      types.ForceReply)


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
