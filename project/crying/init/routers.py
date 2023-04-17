from aiogram import Dispatcher
from loguru import logger

from ..apps.bot.handlers import register_common_routers
from ..apps.bot.handlers.admin import register_admin_routers
from ..apps.bot.handlers.error import errors
from ..config import Settings


async def setup_routers(
        dp: Dispatcher,
        settings: Settings,
):
    # Handling errors
    dp.include_router(errors.router)

    # Admin handlers
    register_admin_routers(dp, settings.bot.admins)

    # Common handlers
    register_common_routers(dp)

    logger.info("Routers setup complete")
