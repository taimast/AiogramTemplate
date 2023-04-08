from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from aiogram import Bot
from aiogram.utils import deep_linking
from order_bot.db.models import User

from ..keyboards.common import common_kbs

if TYPE_CHECKING:
    from ..locales.stubs.ru.stub import TranslatorRunner


@dataclass
class Order:
    info: str
    name: str
    type: str
    user_id: int
    chat_id: int
    message_id: int | None = None
    manager_id: int | None = None

    def get_request(self, l10n: TranslatorRunner):
        return l10n.order.manager.get_request(
            name=self.name,
            order_info=self.info,
            type=self.type
        )

    async def edit_message(self, bot: Bot, text: str, reply_markup=None):
        await bot.edit_message_text(
            text=text,
            chat_id=self.chat_id,
            message_id=self.message_id,
            reply_markup=reply_markup
        )

    async def send(self, bot: Bot, l10n: TranslatorRunner):
        link = await deep_linking.create_start_link(bot, f"secret_{self.user_id}")
        text = self.get_request(l10n)
        message = await bot.send_message(
            chat_id=self.chat_id,
            text=text,
            reply_markup=common_kbs.connect(link, l10n)
        )
        self.message_id = message.message_id

    async def resend(self, bot: Bot, l10n: TranslatorRunner):
        self.manager_id = None
        link = await deep_linking.create_start_link(bot, f"secret_{self.user_id}")
        text = self.get_request(l10n)
        await self.edit_message(
            bot,
            text=text,
            reply_markup=common_kbs.connect(link, l10n)
        )

    async def take(self, manager: User, bot: Bot, l10n: TranslatorRunner):
        self.manager_id = manager.id
        text = l10n.order.manager.take(
            manager_name=manager.name,
            name=self.name,
            order_info=self.info,
            type=self.type
        )
        await self.edit_message(bot, text, reply_markup=common_kbs.taken(self.user_id, l10n))

    async def done(self, manager_name: str, bot: Bot, l10n: TranslatorRunner):
        text = l10n.order.manager.done(
            manager_name=manager_name,
            name=self.name,
            order_info=self.info,
            type=self.type
        )
        await self.edit_message(bot, text)
