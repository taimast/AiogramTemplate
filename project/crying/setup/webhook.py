import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from loguru import logger

from ..config import Settings


async def start_webhook(bot: Bot, dp: Dispatcher, settings: Settings):
    """Start webhook."""
    # Disable aiohttp logs
    logging.getLogger("aiohttp").setLevel(logging.WARNING)

    # Set webhook
    await bot.set_webhook(
        certificate=settings.webhook.get_certfile(),
        url=settings.webhook.url,
        drop_pending_updates=True,
        allowed_updates=dp.resolve_used_update_types(),
    )

    # Create aiohttp application
    app = web.Application()
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(
        app, path=settings.webhook.path
    )

    # Configure startup and shutdown processes
    setup_application(app, dp)

    # Start aiohttp
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

    logger.info("Webhook started")
    # Run forever
    await asyncio.Future()
