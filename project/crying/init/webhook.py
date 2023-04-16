import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from project.crying.config import Settings


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
