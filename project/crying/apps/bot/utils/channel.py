import re

from aiogram import Bot
from loguru import logger


def parse_channel_link(text: str) -> tuple[str, str]:
    skin, username = text.split()
    if '@' in username:
        username = username.replace('@', '')
    else:
        try:
            username = re.findall(r"t\.me/(.+)", username)[0]
        except Exception as e:
            logger.warning(e)
    return skin, username


async def is_subscribed_to_channel(user_id, bot: Bot, subscription_channels: list) -> bool:
    for channel in subscription_channels:
        try:
            member = await bot.get_chat_member(chat_id=channel.username, user_id=user_id)
            if member.status in ('left', 'kicked'):
                return False
        except Exception as e:
            logger.warning(f"{channel}|{e}")
            pass
    return True
