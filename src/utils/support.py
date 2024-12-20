from dataclasses import dataclass, field
from typing import TypeAlias

from aiogram import Bot, html
from aiogram.types import Message
from aiogram.types.user import User
from bidict import bidict

from src.apps.bot.keyboards.common import common_kbs

UserID: TypeAlias = int
ThreadID: TypeAlias = int


@dataclass
class SupportMessageInfo:
    to_user_id: UserID | None = None
    to_thread_id: ThreadID | None = None
    disconnect_user: bool = False
    is_disconnected_user: bool = False
    close_thread: bool = False


@dataclass
class SupportConnector:
    bot: Bot
    chat_id: int
    sessions: bidict[UserID, ThreadID] = field(default_factory=bidict)
    disconnected_users: dict[UserID, ThreadID] = field(default_factory=dict)
    closed_sessions: dict[UserID, ThreadID] = field(default_factory=dict)

    close_thread_command: str = "/close_thread"
    disconnect_user_command: str = "/disconnect_user"

    def get_thread_id(self, user_id: UserID) -> ThreadID | None:
        return self.sessions.get(user_id)

    def get_user_id(self, thread_id: ThreadID) -> UserID | None:
        return self.sessions.inv.get(thread_id)

    def get_message_info(self, message: Message) -> SupportMessageInfo | None:
        if (
            not message.forum_topic_created
            and message.message_thread_id
            and (message.chat.id == self.chat_id)
        ):
            user_id = self.get_user_id(message.message_thread_id)
            if not user_id:
                return None

            close_thread = False
            disconnect_user = False
            if message.text:
                if message.text.startswith(self.close_thread_command):
                    close_thread = True
                elif message.text.startswith(self.disconnect_user_command):
                    disconnect_user = True

            return SupportMessageInfo(
                to_user_id=user_id,
                close_thread=close_thread,
                disconnect_user=disconnect_user,
            )

        if (
            message.from_user
            and message.chat.id != self.chat_id
            and (thread_id := self.get_thread_id(message.from_user.id))
        ):
            return SupportMessageInfo(
                to_thread_id=thread_id,
                is_disconnected_user=message.from_user.id in self.disconnected_users,
            )

        return None

    async def send_to_thread(
        self,
        message: Message,
        thread_id: ThreadID,
    ):
        return await message.copy_to(
            self.chat_id,
            message_thread_id=thread_id,
            reply_markup=common_kbs.thread_support(),
        )

    async def send_to_user(
        self,
        message: Message,
        user_id: UserID,
    ):
        if user_id in self.disconnected_users:
            self.disconnected_users.pop(user_id)
        return await message.copy_to(user_id)

    async def create_thread(self, user: User) -> ThreadID:
        if user.id in self.sessions:
            return self.sessions[user.id]
        if user.id in self.disconnected_users:
            thread_id = self.disconnected_users.pop(user.id)
            await self.bot.send_message(
                self.chat_id,
                f"User {user.full_name} reconnected to a thread.",
            )
            await self.bot.send_message(
                self.chat_id,
                "User reconnected to a thread.",
                message_thread_id=thread_id,
            )
            return thread_id

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

        start_text = (
            html.bold(f"User {user.mention_html()} created a new thread.\n\n")
            + html.italic(f"{self.close_thread_command} - Close Thread\n")
            + html.italic(f"{self.disconnect_user_command} - Disconnect User\n")
        )
        start_msg = await self.bot.send_message(
            self.chat_id,
            message_thread_id=thread.message_thread_id,
            text=start_text,
        )
        start_msg.pin()

        return thread.message_thread_id

    async def close_thread(self, user_id: int):
        thread_id = self.sessions.pop(user_id)
        await self.bot.close_forum_topic(self.chat_id, thread_id)
        await self.bot.send_message(
            self.chat_id,
            f"User {user_id} closed a thread.",
        )
        await self.bot.send_message(
            user_id,
            "Your thread was closed.",
        )
        self.closed_sessions[user_id] = thread_id

    async def disconnect_user(self, user_id: int):
        thread_id = self.sessions[user_id]
        self.disconnected_users[user_id] = thread_id
        await self.bot.send_message(
            self.chat_id,
            f"User {user_id} was disconnected.",
        )
        await self.bot.send_message(
            self.chat_id,
            "User was disconnected.",
            message_thread_id=thread_id,
        )
        await self.bot.send_message(
            user_id,
            "You were disconnected.",
        )
        return thread_id
