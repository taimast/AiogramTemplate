import asyncio
from collections import deque
from dataclasses import dataclass, field
from typing import ClassVar, Self

from aiogram import types, Bot
from aiogram.exceptions import TelegramRetryAfter
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
    update_interval: float = 10
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

    async def update_status(self):
        self.current_emoji = "⏳ In progress" if self.current_emoji == "⌛ In progress" else "⌛ In progress"
        try:
            await self.status_message.edit_text(
                self.status_template,
                reply_markup=self.cancel_markup
            )
        except Exception as e:
            logger.warning(f"Error while updating status message: {e}")

    async def live_updating_status(self):
        while True:
            await asyncio.sleep(self.update_interval)
            await self.update_status()

    async def send(self, bot: Bot, user_id: int, message: types.Message, rm=None):
        sm = await bot.copy_message(
            user_id,
            message.chat.id,
            message.message_id,
            reply_markup=rm
        )
        self.messages.append((user_id, sm.message_id))
        self.success += 1

    async def send_to_all(self, bot: Bot, user_ids: list[int], message: types.Message):
        for user in user_ids:
            try:
                await self.send(bot, user, message)
            except Exception as e:
                self.failed += 1
                logger.warning(f"Error while sending message to {user}: {e}")

            except TelegramRetryAfter as e:
                logger.warning(f"Telegram API limit exceeded: {e}")
                await asyncio.sleep(e.retry_after)
                try:
                    await self.send(bot, user, message)
                except Exception as e:
                    self.failed += 1
                    logger.error(f"Error while sending message to {user}: {e}")
            finally:
                await asyncio.sleep(self.send_interval)

    async def send_notifications(self, bot: Bot, user_ids: list[int], message: types.Message, rm=None):
        batch_size = 25  # количество сообщений в одной партии
        sleep_time = 1  # время паузы в секундах между партиями

        for i in range(0, len(user_ids), batch_size):
            tasks = []
            for user in user_ids[i:i + batch_size]:
                tasks.append(asyncio.create_task(self.send(bot, user, message, rm)))
            results = await asyncio.gather(*tasks, return_exceptions=True)

            next_sleep = sleep_time
            for result in results:
                if isinstance(result, TelegramRetryAfter):
                    logger.warning(f"Telegram API limit exceeded: {result}")
                    next_sleep = max(next_sleep, result.retry_after)
                elif isinstance(result, Exception):
                    self.failed += 1
                    logger.error(f"Error while sending message: {result}")

            await asyncio.sleep(next_sleep)

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
