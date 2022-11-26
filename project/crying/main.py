import asyncio
import logging
import time

from aiogram import Bot, F, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from aiogram.webhook.aiohttp_server import setup_application, SimpleRequestHandler
from aiohttp import web
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger

from project.crying.apps.bot.handlers.admin import register_admin_handlers
from project.crying.apps.bot.handlers.common import register_common_handlers
from project.crying.apps.bot.handlers.errors.errors_handlers import register_error
from project.crying.apps.bot.middleware import UserMiddleware
from project.crying.config.cli import CLIArgsSettings
from project.crying.config.config import Settings
from project.crying.config.logg_settings import init_logging, Level
from project.crying.db import init_db, close_db
from project.crying.db.utils.backup import making_backup


async def set_commands(bot: Bot):
    """Установка команд бота"""
    commands = [
        BotCommand(command="/start", description="Стартовое меню"),
        BotCommand(command="/admin", description="Админ панель"),
    ]
    await bot.set_my_commands(commands)


def setup_routers(dp: Dispatcher, settings: Settings):
    """Регистрация обработчиков"""
    # Обработчики общего назначения
    register_common_handlers(dp)

    # Обработчики админки
    register_admin_handlers(dp, settings.bot.admins)

    # Обработчики ошибок
    register_error(dp)


def register_middlewares(dp: Dispatcher):
    """Регистрация middleware"""
    # dp.update.outer_middleware(ThrottlingMiddleware(ttl=0.5))
    user_middleware = UserMiddleware()
    dp.message.middleware(user_middleware)
    dp.callback_query.middleware(user_middleware)

    # Регистрация мидлвари i18n
    # dp.message.middleware(language_middleware)
    # dp.callback_query.middleware(language_middleware)


# Initializing and start Scheduler function
async def start_scheduler():
    """Инициализация и запуск планировщика задач."""
    # Инициализация планировщика
    scheduler = AsyncIOScheduler()

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


async def main():
    # Парсинг аргументов командной строки
    cli_settings = CLIArgsSettings.parse_args()
    cli_settings.update_settings(Settings)
    cli_settings.log.stdout = Level.TRACE

    # Создание объекта конфига
    settings = Settings()

    # Настройка логирования
    init_logging(cli_settings.log)

    # Инициализация базы данных
    await init_db(settings.db)

    # Инициализация бота
    bot = Bot(token=settings.bot.token.get_secret_value(), parse_mode="html")
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.workflow_data.update(settings=settings)

    # Настройка фильтра только для приватных сообщений
    dp.message.filter(F.chat.type == "private")

    # Регистрация обработчиков
    setup_routers(dp)

    # Регистрация мидлварей
    register_middlewares(dp)

    # Запуск планировщика
    await start_scheduler()

    # Установка команд бота
    await set_commands(bot)

    # Запуск бота
    try:
        if not cli_settings.webhook:
            logger.info("Запуск бота в обычном режиме")
            await bot.delete_webhook()
            await dp.start_polling(
                bot,
                skip_updates=True,
                allowed_updates=dp.resolve_used_update_types(),
            )

        else:
            logger.info("Запуск бота в вебхук режиме")
            await start_webhook(bot, dp, settings)
    finally:
        await bot.session.close()
        await dp.storage.close()
        await close_db()


if __name__ == "__main__":
    for i in range(1, 4):
        try:
            asyncio.run(main())
        except Exception as e:
            logger.exception(e)
            logger.error(f"Бот упал с ошибкой, перезапуск через 5 секунд... Попытка {i}/3")
            time.sleep(5)
        else:
            break
    asyncio.run(main())
