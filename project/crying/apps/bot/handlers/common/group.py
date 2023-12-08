from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram import Router, types, Bot
from aiogram.enums import ChatMemberStatus
from aiogram.filters import ChatMemberUpdatedFilter, ADMINISTRATOR
from loguru import logger

from project.crying.config import Settings

if TYPE_CHECKING:
    pass

router = Router(name=__name__)


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

    # settings.bot.chat_id = update.chat.id
    # settings.dump()
    logger.success(f"Chat id: {update.chat.id} saved")
