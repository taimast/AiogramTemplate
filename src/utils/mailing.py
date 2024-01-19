import asyncio
from collections import deque
from dataclasses import dataclass, field
from typing import ClassVar, Self

from aiogram import types, Bot
from aiogram.utils import markdown as md
from loguru import logger

ChatID = int
MessageID = int


@dataclass
class Mailing:
    success: int = 0
    failed: int = 0
    status_message: types.Message | None = None
    current_emoji: str = "⏳ In progress"
    update_interval: float = 0.6
    send_interval: float = 0.4
    delete_interval: float = 0.2

    cancel_markup: types.InlineKeyboardMarkup | None = None
    messages: list[(ChatID, MessageID)] = field(default_factory=list)
    mailings: ClassVar[deque[Self]] = deque(maxlen=1)

    @classmethod
    def get_last(cls) -> Self | None:
        return cls.mailings[-1] if cls.mailings else None

    @property
    def status_template(self):
        return f"📨 Total: {md.hcode(self.success + self.failed)}\n" \
               f"✅ Success: {md.hcode(self.success)}\n" \
               f"🚫 Failed: {md.hcode(self.failed)}\n\n" \
               f"{self.current_emoji}\n"

    async def init_status_message(self, message: types.Message):
        self.status_message = await message.answer(
            self.status_template,
            reply_markup=self.cancel_markup
        )

    async def live_updating_status(self):
        while True:
            await asyncio.sleep(self.update_interval)
            self.current_emoji = "⏳ In progress" if self.current_emoji == "⌛ In progress" else "⌛ In progress"
            try:
                await self.status_message.edit_text(
                    self.status_template,
                    reply_markup=self.cancel_markup
                )
            except Exception as e:
                logger.warning(f"Error while updating status message: {e}")

    async def send(self, bot: Bot, user_id: int, message: types.Message):
        try:
            sm = await bot.copy_message(
                user_id,
                message.chat.id,
                message.message_id,
            )
            self.messages.append((user_id, sm.message_id))
            self.success += 1
        except Exception as e:
            self.failed += 1
            logger.warning(f"Error while sending message to {user_id}: {e}")

    async def send_to_all(self, bot: Bot, user_ids: list[int], message: types.Message):
        for user in user_ids:
            await self.send(bot, user, message)
            await asyncio.sleep(self.send_interval)

    async def done(self):
        await self.status_message.edit_text(
            self.status_template.replace(self.current_emoji, "✅ Done")
        )

    async def cancel(self):
        await self.status_message.edit_text(
            self.status_template.replace(self.current_emoji, "🚫 Canceled")
        )

    async def retracted_status(self):
        await self.status_message.edit_text(
            self.status_template.replace(self.current_emoji, "🔄 Retracted")
        )

    # Отменить последную рассылку
    # Также запускается как send и обновляет статусы обратно
    async def retract(self, bot: Bot):
        self.failed = 0
        copy_messages = self.messages.copy()
        for chat_id, message_id in copy_messages:
            try:
                await bot.delete_message(chat_id, message_id)
                self.success -= 1
                self.messages.remove((chat_id, message_id))
            except Exception as e:
                self.failed += 1
                logger.warning(
                    f"Error while deleting message {message_id} from {chat_id}: {e}"
                )
            finally:
                await asyncio.sleep(self.delete_interval)
