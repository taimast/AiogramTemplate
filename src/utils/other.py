import asyncio
import io
import os
import time
import zipfile
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, TypeVar, Generic

from aiogram import types, Bot
from loguru import logger

from src.config import Settings


def get_archive():
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w') as zip_file:
        for root, dirs, files in os.walk('.'):
            for file in files:
                zip_file.write(os.path.join(root, file))
    buffer.seek(0)
    document = types.BufferedInputFile(buffer.getvalue(), filename='archive.zip')
    return document


async def send_start_info(settings: Settings, bot: Bot, only_text: bool = True):
    if not settings.bot.admins:
        return
    admin_id = next(iter(settings.bot.admins))
    username = (await bot.me()).username
    info_text = f"Bot @{username} started"
    logger.warning(info_text)
    if only_text:
        await bot.send_message(admin_id, info_text)
        return
    document = await asyncio.to_thread(get_archive)
    await bot.send_document(
        admin_id,
        document,
        caption=info_text,
    )


T = TypeVar('T')


# Структура для вызова функции по банчам
@dataclass
class BatchExecutor(Generic[T]):
    func: Callable[[T, Any], Awaitable[Any]]
    objs: list[T]
    args: tuple = ()
    kwargs: dict = field(default_factory=dict)
    batch_size: int = 30
    sleep_time: int = 1

    async def call(self, obj: T):
        return await self.func(obj, *self.args, **self.kwargs)

    async def safe_call(self, obj: T):
        try:
            return await self.call(obj)
        except Exception as e:
            logger.exception(f"Не удалось обработать объект {obj}: {e}")
            return None

    async def batched_call(self) -> list[Any]:
        results = []
        for _from in range(0, len(self.objs), self.batch_size):
            _to = _from + self.batch_size
            batch = self.objs[_from:_to]
            start_time = time.time()
            tasks = [self.safe_call(obj) for obj in batch]
            results.extend(await asyncio.gather(*tasks))
            elapsed_time = time.time() - start_time
            next_sleep = self.sleep_time - elapsed_time
            if next_sleep > 0:
                await asyncio.sleep(next_sleep)

        return results
