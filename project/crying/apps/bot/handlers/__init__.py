from aiogram import Dispatcher, Router

from . import common
from .error import errors


# from aiogram_admin.filters.channel_subscription_filter import ChannelSubscriptionFilter


def register_common_routers(dp: Dispatcher):
    router = Router(name="common")
    # router.message.filter(ChannelSubscriptionFilter())
    # router.callback_query.filter(ChannelSubscriptionFilter())
    router.include_router(common.router)
    dp.include_router(router)
