from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram import Bot
from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from src.apps.bot.keyboards.common import helper_kbs
from src.utils.subscribe import is_subscribed

if TYPE_CHECKING:
    from src.locales.stubs.ru.stub import TranslatorRunner


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
        is_sub = await is_subscribed(bot, message.chat.id, subscribe_channels)
        if not is_sub:
            await message.answer(
                l10n.channel.subscribe(),
                reply_markup=helper_kbs.subscribe_channel(subscribe_channels, l10n)
            )
        return is_sub
