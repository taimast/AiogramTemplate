import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import BotCommandScopeDefault, BotCommandScopeChat
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram_admin import setup_admin_handlers
from aiohttp import web
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger

from project.crying.apps.bot.commands.bot_commands import AdminCommandsCollection, SuperAdminCommandsCollection, \
    BaseCommandsCollection
from project.crying.apps.bot.handlers import register_common_routers
from project.crying.apps.bot.handlers.admin import register_admin_routers
from project.crying.apps.bot.handlers.error import errors
from project.crying.apps.bot.middleware import L10nMiddleware, UserMiddleware
from project.crying.config import Settings, TIME_ZONE
from project.crying.db.models import ChannelForSubscription, User
from project.crying.db.utils.backup import making_backup


async def set_commands(bot: Bot, settings: Settings):
    """ Установка команд бота. """

    async def _set_commands(commands, scope):
        try:
            await bot.set_my_commands(commands, scope=scope)
        except TelegramBadRequest as e:
            logger.warning(f"Can't set commands for {scope}: {e}")

    await _set_commands(BaseCommandsCollection, scope=BotCommandScopeDefault())
    for admin in settings.bot.admins:
        await _set_commands(AdminCommandsCollection, scope=BotCommandScopeChat(chat_id=admin))
    for super_admin in settings.bot.super_admins:
        await _set_commands(SuperAdminCommandsCollection, scope=BotCommandScopeChat(chat_id=super_admin))


async def setup_routers(dp: Dispatcher, settings: Settings):
    """Регистрация обработчиков"""

    # Обработчики ошибок
    dp.include_router(errors.router)

    # Обработчики общего назначения
    register_common_routers(dp)

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


def setup_middlewares(dp: Dispatcher, l10n_middleware: L10nMiddleware):
    # Мидлварь для получения пользователя
    user_middleware = UserMiddleware()
    dp.message.middleware(user_middleware)
    dp.callback_query.middleware(user_middleware)

    # Мидлварь для получения языка пользователя
    # dp.message.middleware(language_middleware)
    # dp.callback_query.middleware(language_middleware)

    # Мидлварь для локализации
    # l10n_middleware = L10nMiddleware(
    #     loader=FluentResourceLoader(str(LOCALES_DIR / "{locale}")),
    #     default_locale="ru",
    #     locales=["en"],
    #     resource_ids=["common.ftl"]
    # )
    # logger.info("Загружены локали: " + ", ".join(l10n_middleware.locales))
    dp.message.middleware(l10n_middleware)
    dp.callback_query.middleware(l10n_middleware)


def start_scheduler():
    """Инициализация и запуск планировщика задач."""
    # Инициализация планировщика
    scheduler = AsyncIOScheduler(timezone=TIME_ZONE)

    # Создание бекапа базы данных
    scheduler.add_job(making_backup, 'cron', hour=0, minute=0)

    # Запуск планировщика
    scheduler.start()


async def start_webhook(bot: Bot, dp: Dispatcher, settings: Settings):
    """Start webhook."""
    # Выключаем логи от aiohttp
    logging.getLogger("aiohttp").setLevel(logging.WARNING)

    # Установка вебхука
    await bot.set_webhook(
        certificate=settings.webhook.get_certfile(),
        url=settings.webhook.url,
        drop_pending_updates=True,
        allowed_updates=dp.resolve_used_update_types(),
    )

    # Создание запуска aiohttp
    app = web.Application()
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(
        app, path=settings.webhook.path
    )
    # Конфигурация startup и shutdown процессов
    setup_application(app, dp)

    # Запуск aiohttp
    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(
        runner,
        host=settings.webhook.host,
        port=settings.webhook.port,
        ssl_context=settings.webhook.get_ssl_context(),
    )
    # web.run_app(app, host=config.webhook.host, port=config.webhook.port)
    await site.start()

    # Бесконечный цикл
    await asyncio.Event().wait()
    # todo L1 09.11.2022 1:32 taima: убрать этот костыль
