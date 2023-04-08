from __future__ import annotations

from pprint import pformat
from typing import TYPE_CHECKING

from aiogram import Router, types, Bot
from aiogram.enums import ChatMemberStatus
from aiogram.filters import ChatMemberUpdatedFilter, ADMINISTRATOR
from loguru import logger

from .....config import Settings

if TYPE_CHECKING:
    pass

router = Router()


@router.my_chat_member(ChatMemberUpdatedFilter(ADMINISTRATOR))
async def my_chat_member(update: types.Message, bot: Bot, settings: Settings):
    is_admin_group = False
    for admin in settings.bot.super_admins:
        try:
            member = await bot.get_chat_member(update.chat.id, admin)
        except Exception as e:
            logger.warning(e)
            continue
        if member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR):
            is_admin_group = True
            break
    if not is_admin_group:
        return

    settings.bot.chat_id = update.chat.id
    settings.dump()
    logger.success(f"Chat id: {update.chat.id} saved")


@router.chat_join_request()
async def chat_join_request(update: types.ChatJoinRequest, bot: Bot, settings: Settings):
    print("chat_join_request", pformat(update.dict()))


@router.my_chat_member()
async def my_chat_member(update: types.Message, bot: Bot, settings: Settings):
    print("my_chat_member", pformat(update.dict()))


@router.chat_member()
async def chat_member(update: types.Message, bot: Bot, settings: Settings):
    print("chat_member", pformat(update.dict()))


@router.message()
async def message(update: types.Message, bot: Bot, settings: Settings):
    print("message", pformat(update.dict()))
