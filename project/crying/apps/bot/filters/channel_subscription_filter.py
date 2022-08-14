from aiogram import types, Bot
from aiogram.dispatcher.filters import BaseFilter

from project.crying.apps.bot.markups.common import common_markups
from project.crying.apps.bot.middleware.language import _
from project.crying.apps.bot.utils import is_subscribed_to_channel, TempData
from project.crying.db.models import User


class ChannelSubscriptionFilter(BaseFilter):
    async def __call__(self, message: types.Message | types.CallbackQuery,
                       user: User,
                       bot: Bot,
                       temp_data: TempData) -> bool:
        if isinstance(message, types.CallbackQuery):
            message = message.message

        if not await is_subscribed_to_channel(user.id, bot, temp_data.subscription_channels):
            await message.answer(_(f"📍 Для того, чтобы пользоваться ботом, нужно подписаться на каналы:"),
                                 reply_markup=common_markups.is_subscribed_to_channel(temp_data.subscription_channels))
            return False
        return True
