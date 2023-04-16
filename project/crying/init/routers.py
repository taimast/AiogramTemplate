from aiogram import Dispatcher
from aiogram_admin import setup_admin_handlers

from project.crying.apps.bot.handlers import register_common_routers
from project.crying.apps.bot.handlers.admin import register_admin_routers
from project.crying.apps.bot.handlers.error import errors
from project.crying.config import Settings
from project.crying.db.models import ChannelForSubscription, User


async def setup_routers(
        dp: Dispatcher,
        settings: Settings,
        *,
        check_subscriptions=True,
        check_admins=True,
        check_super_admins=True,
):
    """Регистрация обработчиков"""

    # Обработчики ошибок
    dp.include_router(errors.router)

    # Обработчики админки
    register_admin_routers(dp, settings.bot.admins)
    # Обработчики админки
    await setup_admin_handlers(
        dp=dp,
        admins=settings.bot.admins,
        super_admins=settings.bot.super_admins,
        SubsChat=ChannelForSubscription,
        User=User,
        admin_command="base_admin",
    )
    # Обработчики общего назначения
    register_common_routers(dp)
