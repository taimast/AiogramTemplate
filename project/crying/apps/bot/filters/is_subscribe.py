from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram import Bot
from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from project.crying.apps.bot.keyboards.common import common_kbs
from project.crying.utils.subscribe import is_subscribe

if TYPE_CHECKING:
    from project.crying.locales.stubs.ru.stub import TranslatorRunner


class IsSubscribeFilter(BaseFilter):

    async def __call__(
            self,
            message: Message | CallbackQuery,
            bot: Bot,
            subscribe_channels: list[str],
            l10n: TranslatorRunner

    ) -> bool:
        if isinstance(message, CallbackQuery):
            message = message.message
        is_subscribed = await is_subscribe(bot, message.chat.id, subscribe_channels)
        if not is_subscribed:
            await message.answer(
                l10n.channel.subscribe(),
                reply_markup=common_kbs.subscribe_channel(subscribe_channels, l10n)
            )
        return is_subscribed

