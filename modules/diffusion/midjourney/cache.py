from dataclasses import dataclass

import CacheToolsUtils as ctu
import aiohttp
import orjson
from aiogram import Bot
from aiogram.types import BufferedInputFile
from cachetools import TTLCache
from redis import Redis

from diffusion_bot.apps.diffusion.midjourney.response import TriggerID, ProcessingTrigger, Trigger, MsgID
from diffusion_bot.apps.share.cache_manager import CACHE_MANAGER

MJ_TRIGGERS_PROCESSING_CACHE: TTLCache[
    TriggerID, ProcessingTrigger
] = CACHE_MANAGER.midjourney_triggers_processing_cache
MJ_TRIGGERS_ID_CACHE: TTLCache[MsgID, Trigger] = CACHE_MANAGER.midjourney_triggers_id_cache


class PrefixedRedisCache(ctu.PrefixedRedisCache):
    def _serialize(self, s):
        # if not serializable set NOne
        return orjson.dumps(s, default=lambda o: None)

    def _deserialize(self, s):
        return orjson.loads(s)

    def _key(self, key):
        return orjson.dumps(key)


Cache = PrefixedRedisCache


@dataclass
class CacheAnimation:
    url: str
    file_id: str | None = None

    async def get_file_id(self, bot: Bot) -> str:
        if self.file_id:
            return self.file_id
        file = await download_file(self.url)
        file_id = await bot.send_animation(
            chat_id=269019356,
            animation=BufferedInputFile(file, "animation.gif")
        )
        self.file_id = file_id.animation.file_id
        return self.file_id


class MJCache:

    def __init__(self, redis: Redis, ttl: int = 60 * 60 * 24 * 3):
        self.redis = redis
        self.processing_triggers: Cache[TriggerID, ProcessingTrigger] = Cache(
            redis,
            prefix="processing.triggers.",
            ttl=ttl
        )
        self.done_triggers: Cache[MsgID, Trigger] = Cache(
            redis,
            prefix="done.triggers.",
            ttl=ttl
        )
        self.imagine_animation = CacheAnimation(
            "https://cdn.dribbble.com/users/1514097/screenshots/3457456/media/b1cfddae9e7b9645b9cde7ad9ee4f6bf.gif"
        )
        self.variation_animation = CacheAnimation(
            "https://usagif.com/wp-content/uploads/loading-9.gif"
        )

    def get_processing_trigger(self, trigger_id: TriggerID) -> ProcessingTrigger | None:
        try:
            pt = MJ_TRIGGERS_PROCESSING_CACHE.get(trigger_id)
            if pt:
                return pt

            data = self.processing_triggers[trigger_id]
            return ProcessingTrigger(**data)
        except KeyError:
            return None

    def get_done_trigger(self, msg_id: MsgID) -> Trigger | None:
        try:
            trigger = MJ_TRIGGERS_ID_CACHE.get(msg_id)
            if trigger:
                return trigger

            data = self.done_triggers[msg_id]
            return Trigger(**data)
        except KeyError:
            return None

    def set_processing_trigger(self, processing_trigger: ProcessingTrigger):
        MJ_TRIGGERS_PROCESSING_CACHE[processing_trigger.trigger_id] = processing_trigger
        self.processing_triggers[processing_trigger.trigger_id] = processing_trigger.__dict__

    def set_done_trigger(self, trigger: Trigger):
        MJ_TRIGGERS_ID_CACHE[trigger.msg_id] = trigger
        self.done_triggers[trigger.msg_id] = trigger.__dict__


async def download_file(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                return await resp.read()
