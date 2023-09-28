from __future__ import annotations

import typing
from functools import cache

from aiogram import Bot
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from .base import BaseDispatcher
from .client import Client
from .methods import CachedMethods
from .observer import Observable
from ...db.models import Project, Account

UserID = ChatID = int


@cache
def get_lock(key: typing.Any) -> asyncio.Lock:
    """Получение блокировки по ключу"""
    return asyncio.Lock()


class Dispatcher(BaseDispatcher, Observable, CachedMethods):
    """Диспетчер аккаунта"""

    def __init__(
            self,
            client: Client,
            bot: Bot,
            account: Account,
    ):
        super().__init__(client)
        self.bot = bot
        self.account = account

    async def message_handler(self, client: Client, message: Message):
        pass

    async def update_account(self, session: AsyncSession):
        query = select(Account).options(
            joinedload(Account.projects).joinedload(Project.user),
            joinedload(Account.projects).joinedload(Project.chats),
        ).where(Account.id == self.account.id)
        result = await session.execute(query)
        self.account = result.unique().scalar_one()

    @classmethod
    async def update_dispatchers(
            cls,
            session: AsyncSession,
            user_dispatchers: dict[int, Dispatcher]
    ):
        for dispatcher in user_dispatchers.values():
            await dispatcher.update_account(session)

    async def start(self):
        self.add_handler(MessageHandler(self.message_handler))
        await super().start()
        await self.client.send_message("me", "Dispatcher started")


import asyncio


async def main():
    async  with Client() as client:
        client.get_


if __name__ == '__main__':
    asyncio.run(main())
