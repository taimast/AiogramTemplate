from __future__ import annotations

from aiogram import Bot, F, Router, types
from loguru import logger

on = Router(name=__name__)
on.message.filter(F.chat.type != "private")


@on.chat_member()
async def chat_member(update: types.ChatMemberUpdated, bot: Bot):
    logger.debug("chat_member")


@on.my_chat_member()
async def my_chat_member(update: types.ChatMemberUpdated, bot: Bot):
    logger.debug("my_chat_member")


# @on.message()
# async def message(
#     update: types.Message,
#     bot: Bot,
# ):
#     pprint(update.model_dump())
