import asyncio
import logging

from aiogram import Bot, F, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from aiogram.webhook.aiohttp_server import setup_application, SimpleRequestHandler
from aiohttp import web
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from project.crying.apps.bot.handlers.admin import register_admin_handlers
from project.crying.apps.bot.handlers.common import register_common_handlers
from project.crying.apps.bot.handlers.errors.errors_handlers import register_error
from project.crying.apps.bot.middleware import BotMiddleware, ThrottlingMiddleware, UserMiddleware
from project.crying.apps.bot.middleware.language import language_middleware
from project.crying.apps.bot.utils import add_me
from project.crying.apps.bot.utils.bot import TempData
from project.crying.config.cli import cli_settings
from project.crying.config.config import config
from project.crying.config.logg_settings import init_logging
from project.crying.db import init_db
from project.crying.db.models import Channel
from project.crying.db.utils.backup import making_backup


async def set_commands(bot: Bot):
    """Установка команд бота"""
    commands = [
        BotCommand(command="/start", description="Стартовое меню"),
        BotCommand(command="/admin", description="Админ панель"),
    ]
    await bot.set_my_commands(commands)


async def main():
    # Настройка логирования
    init_logging(**cli_settings.log.dict())

    # Инициализация базы данных
    await init_db()

    # Инициализация бота
    bot = Bot(token=config.bot.token.get_secret_value(), parse_mode="html")
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.startup.register(add_me)

    # Настройка фильтра только для приватных сообщений
    dp.message.filter(F.chat.type == "private")

    # Регистрация обработчиков
    register_admin_handlers(dp)
    register_common_handlers(dp)
    register_error(dp)

    # Регистрация мидлварей
    dp.update.outer_middleware(BotMiddleware())
    dp.update.outer_middleware(ThrottlingMiddleware(ttl=0.5))
    user_middleware = UserMiddleware()
    dp.message.outer_middleware(user_middleware)
    dp.callback_query.outer_middleware(user_middleware)

    # Регистрация мидлвари i18n
    dp.message.middleware(language_middleware)

    # Инициализация планировщика задач
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")

    # Создание фоновых задач
    scheduler.add_job(making_backup, "interval", hours=1)

    # Создание временных переменных
    temp_data = TempData(
        subscription_channels=await Channel.all(),
        mail_sender=None,
        bot_running=True,
    )

    # Установка команд бота
    await set_commands(bot)

    # Запуск планировщика
    scheduler.start()

    # Запуск бота
    try:
        if not config.webhook:
            logging.info("Запуск бота в обычном режиме")
            await bot.delete_webhook()
            await dp.start_polling(
                bot,
                skip_updates=True,
                allowed_updates=dp.resolve_used_update_types(),
                temp_data=temp_data,
            )

        else:
            logging.info("Запуск бота в вебхук режиме")

            # Выключаем логи от aiohttp
            logging.getLogger("aiohttp").setLevel(logging.WARNING)

            # Установка вебхука
            await bot.set_webhook(
                certificate=config.webhook.get_certfile(),
                url=config.webhook.url,
                drop_pending_updates=True,
                allowed_updates=dp.resolve_used_update_types(),
            )

            # Создание запуска aiohttp
            app = web.Application()
            # SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=config.webhook.path)
            SimpleRequestHandler(dispatcher=dp, bot=bot, temp_data=temp_data).register(
                app, path=config.webhook.path
            )

            # setup_application(app, dp, temp_data=temp_data, _=i18n.gettext)
            setup_application(app, dp)

            runner = web.AppRunner(app)
            await runner.setup()

            site = web.TCPSite(
                runner,
                host=config.webhook.host,
                port=config.webhook.port,
                ssl_context=config.webhook.get_ssl_context(),
            )

            await site.start()

            # Бесконечный цикл
            await asyncio.Event().wait()

    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
