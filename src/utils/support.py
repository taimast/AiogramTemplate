from dataclasses import dataclass, field
from typing import TypeAlias

from aiogram import Bot
from aiogram.types import Message
from aiogram.types.user import User
from bidict import bidict

UserID: TypeAlias = int
ThreadID: TypeAlias = int


@dataclass
class SupportConnector:
    bot: Bot
    chat_id: int
    sessions: bidict[UserID, ThreadID] = field(default_factory=bidict)
    closed_sessions: dict[UserID, ThreadID] = field(default_factory=dict)

    def get_thread_id(self, user_id: UserID) -> ThreadID | None:
        return self.sessions.get(user_id)

    def get_user_id(self, thread_id: ThreadID) -> UserID | None:
        return self.sessions.inv.get(thread_id)

    async def send_to_thread(
        self,
        message: Message,
        thread_id: ThreadID,
    ):
        return await message.copy_to(
            self.chat_id,
            message_thread_id=thread_id,
        )

    async def send_to_user(
        self,
        message: Message,
        user_id: UserID,
    ):
        return await message.copy_to(user_id)

    async def create_thread(self, user: User) -> ThreadID:
        if user.id in self.sessions:
            return self.sessions[user.id]

        if exist_thread_id := self.closed_sessions.get(user.id):
            await self.bot.reopen_forum_topic(self.chat_id, exist_thread_id)
            self.sessions[user.id] = exist_thread_id
            await self.bot.send_message(
                self.chat_id,
                f"User {user.full_name} reopened a closed thread.",
            )

            return exist_thread_id

        thread = await self.bot.create_forum_topic(self.chat_id, user.full_name)
        self.sessions[user.id] = thread.message_thread_id
        await self.bot.send_message(
            self.chat_id,
            f"User {user.full_name} created a new thread.",
        )
        return thread.message_thread_id

    async def close_thread(self, user: User):
        thread_id = self.sessions.pop(user.id)
        await self.bot.close_forum_topic(self.chat_id, thread_id)
