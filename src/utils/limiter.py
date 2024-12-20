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


class LockManager:
    def __init__(
        self,
        cleanup_interval: int = 60 * 5,
        lock_timeout: int = 5,
    ):
        self.locks = {}
        self.global_lock = asyncio.Lock()
        self.cleanup_interval = cleanup_interval
        self.lock_timeout = lock_timeout
        self.cleanup_task = asyncio.create_task(self.cleanup_locks())

    async def get_lock(self, user_id: int) -> asyncio.Lock:
        async with self.global_lock:
            if user_id not in self.locks:
                self.locks[user_id] = asyncio.Lock()
            return self.locks[user_id]

    async def release_lock(self, user_id: int):
        async with self.global_lock:
            if user_id in self.locks:
                del self.locks[user_id]

    async def clear_all_locks(self):
        async with self.global_lock:
            self.locks.clear()

    async def cleanup_locks(self):
        while True:
            await asyncio.sleep(self.cleanup_interval)
            async with self.global_lock:
                for user_id, lock in list(self.locks.items()):
                    if lock.locked():
                        try:
                            # Wait until the lock is released or timeout occurs
                            async with asyncio.timeout(self.lock_timeout):
                                await lock.acquire()
                            lock.release()
                        except asyncio.TimeoutError:
                            logger.warning(
                                "Timeout waiting for lock release for user {}", user_id
                            )
                    del self.locks[user_id]
                logger.debug("Locks cleanup completed")
