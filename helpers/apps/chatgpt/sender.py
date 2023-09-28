import asyncio
from typing import Callable, Awaitable

from loguru import logger


class QueueSender:
    def __init__(
            self,
            cb: Callable[[str], Awaitable[...]],
            max_messages: int = 1,
            sleep: float = 0.4
    ):
        self.cb = cb
        self.max_messages = max_messages
        self.sleep = sleep
        self._queue = asyncio.Queue()
        self._task = asyncio.create_task(self.sender())

    async def sender(self):
        while True:
            message = await self._queue.get()
            try:
                await self.cb(message)
            except Exception as e:
                logger.warning(e)
                await asyncio.sleep(self.sleep)
                await self.cb(message, parse_mode=None)
            await asyncio.sleep(self.sleep)
            self._queue.task_done()

    async def send(self, message: str):
        if self._queue.qsize() > self.max_messages:
            self._queue.get_nowait()
            self._queue.task_done()
            logger.debug("Queue overflow detected. Clearing queue")
        await self._queue.put(message)

    async def close(self):
        """
        Wait for queue to finish and cancel task
        :return:
        """
        await self._queue.join()
        if not self._task.done():
            self._task.cancel()

    async def force_close(self):
        """
        Cancel task without waiting for queue
        :return:
        """
        if not self._task.done():
            self._task.cancel()
