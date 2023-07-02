from aiogram import Bot
from loguru import logger


async def channel_status_check(bot: Bot, channels: list[str], user_id):
    if channels:
        results = []
        for skin, chat in channels:
            try:
                member = await bot.get_chat_member(chat_id=chat, user_id=user_id)
                if member.status != "left":
                    results.append(True)
                else:
                    results.append(False)
            except Exception as e:
                logger.warning(f"{chat}|{e}")
                results.append(True)
        return all(results)
    return True
