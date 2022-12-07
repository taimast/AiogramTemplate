from aiogram import Dispatcher, Router
from aiogram_admin.filters.channel_subscription_filter import ChannelSubscriptionFilter

from . import common
from .errors import errors


def register_routers(dp: Dispatcher):
    router = Router()
    router.message.filter(ChannelSubscriptionFilter())
    router.callback_query.filter(ChannelSubscriptionFilter())
    router.include_router(common.router)
    router.include_router(errors.router)
    dp.include_router(router)
