from typing import Iterable

from aiogram import Bot
from aiogram.enums import ChatMemberStatus
from loguru import logger


async def is_subscribe(bot: Bot, user_id: int, channels: Iterable[str | int]) -> bool:
    if channels:
        for channel in channels:
            try:
                member = await bot.get_chat_member(channel, user_id)
                if member.status == ChatMemberStatus.LEFT:
                    return False
            except Exception as e:
                logger.warning(e)
                return False
    return True
