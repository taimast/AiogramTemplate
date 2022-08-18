import asyncio
import contextlib
from enum import Enum
from typing import Optional

from aiogram import exceptions, Bot
from aiogram import types
from loguru import logger
from pydantic import BaseModel

from project.crying.apps.bot.markups.admin import admin_markups
from project.crying.config.config import config
from project.crying.db.models import User


class MailStatus(str, Enum):
    run = "run"
    pause = "pause"
    stop = "stop"


class MailSender(BaseModel):
    bot: Bot
    status: MailStatus = MailStatus.run
    message: types.Message
    mail: str
    markup: Optional[types.InlineKeyboardMarkup]

    status_markup: Optional[types.InlineKeyboardMarkup]
    status_message: Optional[types.Message]

    quantity: int = 0
    num: int = 0
    success: int = 0
    failure: int = 0

    class Config:
        arbitrary_types_allowed = True

    def new_mail(self, message: types.Message, mail: str, markup: types.InlineKeyboardMarkup):
        self.message = message
        self.mail = mail
        self.markup = markup
        return self

    async def edit_status_message(self):
        percent = 100 // (self.quantity // self.num)
        await self.status_message.edit_text(f"Выполнено {self.num}/{self.quantity} [{percent} %]:\n"
                                            f"✅ Успешно: {self.success}\n"
                                            f"🚫 Неудачно: {self.failure}", reply_markup=self.status_markup)

    async def sending_mail_status(self):
        while self.status is not MailStatus.stop:
            if self.status is MailStatus.run:
                with contextlib.suppress(exceptions.TelegramBadRequest):
                    await self.edit_status_message()
            await asyncio.sleep(1)
        # await self.edit_status_message()

    async def send_mail(self):
        users = await User.exclude(user_id__in=config.bot.admins)
        self.status_markup = admin_markups.send_mail_done()
        self.status_message = await self.message.answer(f"Выполнено {0}/{len(users)}:\n"
                                                        f"Успешно: {0}\n"
                                                        f"Неуспешно: {0}",
                                                        reply_markup=self.status_markup)
        # return
        # users = await get_mock_users()
        self.quantity = len(users)
        asyncio.create_task(self.sending_mail_status())
        for num, user in enumerate(users, 1):
            self.num = num
            try:
                while True:
                    if self.status is MailStatus.run:
                        await self.bot.send_message(user.id, self.mail, reply_markup=self.markup)
                        logger.trace(f"Рассылка успешно отправлена пользователю [{user.first_name}]{user.id}")
                        self.success += 1
                        break
                    elif self.status is MailStatus.pause:
                        logger.trace(f"Отправка рассылки на паузе")
                        await asyncio.sleep(1)
                    else:
                        logger.trace(f"Рассылка остановлена")
                        self.status_markup = None
                        await self.edit_status_message()
                        return
            except Exception as e:
                self.failure += 1
                logger.warning(e)
            # await self.edit_status_message(num, quantity)
        self.status_markup = None
        await self.edit_status_message()
        await self.message.answer(f"Рассылка отправлена всем {self.quantity} пользователям")
