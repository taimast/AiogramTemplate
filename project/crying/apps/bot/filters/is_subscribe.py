from aiogram import Bot
from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from project.crying.utils.subscribe import is_subscribe


class IsSubscribeFilter(BaseFilter):

    def __init__(self, channels: list[int | str]):
        self.channels = channels

    async def __call__(self, message: Message | CallbackQuery, bot: Bot) -> bool:
        if isinstance(message, CallbackQuery):
            message = message.message
        return await is_subscribe(bot, message.chat.id, self.channels)
