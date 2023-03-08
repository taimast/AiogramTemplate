import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import BotCommandScopeDefault, BotCommandScopeChat
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram_admin import setup_admin_handlers
# from aiogram_admin import setup_admin_handlers
from aiohttp import web
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fluent_compiler.bundle import FluentBundle
from fluentogram import TranslatorHub, FluentTranslator
from loguru import logger

from project.crying.apps.bot.commands.bot_commands import AdminCommandsCollection, SuperAdminCommandsCollection, \
    BaseCommandsCollection
from project.crying.apps.bot.handlers import register_common_routers
from project.crying.apps.bot.handlers.admin import register_admin_routers
from project.crying.apps.bot.handlers.error import errors
from project.crying.apps.bot.middleware import UserMiddleware
from project.crying.apps.bot.middleware.l10n import TranslatorRunnerMiddleware
from project.crying.config import Settings, TIME_ZONE, LOCALES_DIR
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

    # Обработчики общего назначения
    register_common_routers(dp)

    # Обработчики админки
    await setup_admin_handlers(
        dp=dp,
        admins=settings.bot.admins,
        super_admins=settings.bot.super_admins,
        SubsChat=ChannelForSubscription,
        User=User,
        admin_command="base_admin",
    )


def setup_middlewares(dp: Dispatcher):
    # Мидлварь для получения пользователя
    user_middleware = UserMiddleware()
    dp.message.middleware(user_middleware)
    dp.callback_query.middleware(user_middleware)

    # Мидлварь для локализации
    translator_runner_middleware = TranslatorRunnerMiddleware()
    dp.message.middleware(translator_runner_middleware)
    dp.callback_query.middleware(translator_runner_middleware)


def start_scheduler():
    """Инициализация и запуск планировщика задач."""
    # Инициализация планировщика
    scheduler = AsyncIOScheduler(timezone=TIME_ZONE)

    # Создание бекапа базы данных
    scheduler.add_job(making_backup, 'cron', hour=0, minute=0)

    # Запуск планировщика
    scheduler.start()


# todo L1  01.03.2023 15:15 taima: Перенести в config
def init_translator_hub() -> TranslatorHub:
    """Инициализация локализации."""
    en_files = LOCALES_DIR.glob("en/*.ftl")
    ru_files = LOCALES_DIR.glob("ru/*.ftl")
    translator_hub = TranslatorHub(
        {"ru": ("ru", "en"),
         "en": ("en",)},
        [
            FluentTranslator(
                "en",
                translator=FluentBundle.from_files("en-US", filenames=en_files)
            ),
            FluentTranslator(
                "ru",
                translator=FluentBundle.from_files("ru", filenames=ru_files)
            )
        ],
    )
    logger.info("Загружены локали: " + ", ".join(translator_hub.locales_map))
    return translator_hub


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
