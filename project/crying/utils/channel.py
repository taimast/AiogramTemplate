import re

from loguru import logger
from project.crying.apps.bot.temp import SUBSCRIPTION_CHANNELS


def parse_channel_link(text: str) -> tuple[str, str]:
    skin, link = text.split()
    if '@' in link:
        pass
    else:
        try:
            link = '@' + re.findall(r"t\.me/(.+)", link)[0]
        except Exception as e:
            logger.warning(e)
            link = '@' + link
    return skin, link


async def channel_status_check(user_id):
    if SUBSCRIPTION_CHANNELS:
        results = []
        for skin, chat in SUBSCRIPTION_CHANNELS:
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
