import asyncio
import time
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Sequence

from aiolimiter import AsyncLimiter
from loguru import logger


@dataclass
class BatchExecutor[T]:
    """
    Пример использования:
        bot = Bot(...)
        user_ids = [1, 2, 3, 4, 5]
        batch_executor = BatchExecutor(
            func=bot.send_message,
            objs=user_ids,
            args=("Вы приглашены в чат",)
        )
        await batch_executor.batched_call()
    """

    func: Callable[[T, Any], Awaitable[Any]]
    objs: Sequence[T]
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

    @classmethod
    async def create_and_call(
        cls: type[T],
        func: Callable[[T, Any], Awaitable[Any]],
        objs: Sequence[T],
    ) -> list[Any]:
        be = BatchExecutor(func, objs)
        return await be.batched_call()


class RareLimiter[T]:
    def __init__(
        self,
        max_rate: int = 25,
        time_period: int = 1,
    ):
        self.limiter = AsyncLimiter(max_rate, time_period)

    async def __call__(
        self,
        func: Callable[[T], Awaitable[Any]],
        *args,
        **kwargs,
    ):
        async with self.limiter:
            return await func(*args, **kwargs)

    @classmethod
    async def create_and_call(
        cls: type[T],
        func: Callable[[T], Awaitable[Any]],
        *args,
        **kwargs,
    ) -> list[Any]:
        rl = RareLimiter()
        return await rl(func, *args, **kwargs)
