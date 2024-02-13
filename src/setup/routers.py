from aiogram import Dispatcher, F
from aiogram.filters import CommandStart
from loguru import logger

from ..apps.bot.handlers import admin, common, error
from ..config import Settings


async def setup_routers(
        dp: Dispatcher,
        settings: Settings,
):
    # Handling errors
    dp.include_router(error.on)

    # Admin handlers
    admin.on.message.filter(~CommandStart())
    admin.on.message.filter(F.from_user.id.in_(settings.bot.admins))
    admin.on.callback_query.filter(F.from_user.id.in_(settings.bot.admins))
    dp.include_router(admin.on)

    # Common handlers
    dp.include_router(common.on)
    # common.on.include_router(admin.stats.on)
    logger.info("Routers setup complete")
