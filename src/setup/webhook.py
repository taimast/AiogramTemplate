import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import (
    TokenBasedRequestHandler,
    setup_application,
)
from aiohttp import web
from loguru import logger

from src.config import WebhookSettings


async def start_webhook(
    bot: Bot,
    dp: Dispatcher,
    webhook: WebhookSettings,
):
    """Start webhook."""
    # Disable aiohttp logs
    logging.getLogger("aiohttp").setLevel(logging.WARNING)

    # Set webhook
    certificate = webhook.get_certfile()
    await bot.set_webhook(
        certificate=certificate,
        url=webhook.path.format(bot_token=bot.token),
        drop_pending_updates=True,
        allowed_updates=dp.resolve_used_update_types(),
    )
    logger.info(f"Set webhook to {webhook.url}")

    # Create aiohttp application
    app = web.Application()

    bot_settings = {"default": bot.default, "session": bot.session}
    TokenBasedRequestHandler(
        dispatcher=dp,
        bot_settings=bot_settings,
    ).register(app, path=webhook.path)

    # Configure startup and shutdown processes
    setup_application(app, dp)

    # Start aiohttp
    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(
        runner,
        host=webhook.host,
        port=webhook.port,
        ssl_context=webhook.get_ssl_context(),
    )
    # web.run_app(app, host=config.webhook.host, port=config.webhook.port)
    await site.start()

    logger.info(f"Webhook started at {webhook.host}:{webhook.port}{webhook.path}")
    # Run forever
    await asyncio.Future()
