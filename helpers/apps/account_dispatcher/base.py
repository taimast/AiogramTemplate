from loguru import logger
from pyrogram.handlers.handler import Handler

from .client import Client


class BaseDispatcher:

    def __init__(self, client: Client):
        self.client = client
        self.handlers: list[Handler] = []

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()

    async def start(self):
        for handler in self.handlers:
            self.client.add_handler(handler)
        logger.info("Starting client")
        await self.client.start()

    async def stop(self):
        await self.client.__aexit__()

    def add_handler(self, handler: Handler):
        if not isinstance(handler, Handler):
            raise TypeError(f'Handler must be instance of {Handler}')
        self.handlers.append(handler)
