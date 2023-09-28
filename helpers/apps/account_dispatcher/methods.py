import typing
from functools import partial

from asyncache import cachedmethod
from cachetools import TTLCache
from cachetools.keys import hashkey
from loguru import logger
from pyrogram import types

from . import dispatcher

ChatID: typing.TypeAlias = int | str


class Methods:

    async def get_dialogs(self: 'dispatcher.Dispatcher', limit=0) -> list[types.Dialog]:
        logger.success(f"Get dialogs")
        dialogs: list[types.Dialog] = []
        async for dialog in self.client.get_dialogs(limit):
            dialogs.append(dialog)
        return dialogs

    async def get_message(self: 'dispatcher.Dispatcher', chat_id: ChatID, message_id: int) -> types.Message:
        logger.success(f"Get message")
        return await self.client.get_messages(chat_id, message_id)

    async def get_chat(self: 'dispatcher.Dispatcher', chat_id: ChatID) -> types.Chat:
        logger.success(f"Get chat")
        return await self.client.get_chat(chat_id)


class CachedMethods(Methods):
    long_cache = TTLCache(maxsize=128, ttl=60 * 60 * 24)
    medium_cache = TTLCache(maxsize=128, ttl=60 * 60)
    short_cache = TTLCache(maxsize=128, ttl=60)

    @cachedmethod(lambda self: self.short_cache, key=partial(hashkey, 'dialog'))
    async def get_dialogs(self: 'dispatcher.Dispatcher', limit=0) -> list[types.Dialog]:
        logger.debug(f"No cached dialogs")
        return await super().get_dialogs(limit)

    @cachedmethod(lambda self: self.medium_cache, key=partial(hashkey, 'message'))
    async def get_message(self: 'dispatcher.Dispatcher', chat_id: ChatID, message_id: int) -> types.Message:
        logger.debug(f"No cached message")
        return await super().get_message(chat_id, message_id)

    @cachedmethod(lambda self: self.long_cache, key=partial(hashkey, 'chat'))
    async def get_chat(self: 'dispatcher.Dispatcher', chat_id: ChatID) -> types.Chat:
        logger.debug(f"No cached chat")
        return await super().get_chat(chat_id)
