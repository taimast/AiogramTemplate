from aiogram import Dispatcher, F
from loguru import logger

from ..apps.bot.handlers import admin, common, error
from ..config import Settings


async def setup_routers(
        dp: Dispatcher,
        settings: Settings,
):
    # Handling errors
    dp.include_router(error.router)

    # Admin handlers
    admin.router.message.filter(F.from_user.id.in_(settings.bot.admins))
    admin.router.callback_query.filter(F.from_user.id.in_(settings.bot.admins))
    dp.include_router(admin.router)

    # Common handlers
    dp.include_router(common.router)

    logger.info("Routers setup complete")
