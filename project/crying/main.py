import asyncio
from pprint import pformat

from aiogram import Bot, F, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from loguru import logger

from project.crying.config import Settings, CLIArgsSettings, init_logging
from project.crying.init import (
    set_commands,
    setup_middlewares,
    setup_routers,
    setup_scheduler,
    init_translator_hub,
    start_webhook,
    init_db,
    close_db
)


async def on_startup():
    pass


async def on_shutdown():
    pass


# todo L1 TODO 18.02.2023 6:36 taima: Скопировать все из autoanswer
# todo L1 TODO 18.02.2023 7:06 taima: Сделать ввиде раздельных импортируемых модулей
# todo L1 TODO 18.02.2023 7:07 taima: Включить aiogram_admin в проект
async def main():
    # await db.main()
    # return

    # Parse command line arguments
    cli_settings = CLIArgsSettings.parse_args()
    cli_settings.update_settings(Settings)

    # Initialize settings
    settings = Settings()
    logger.info(f"Settings:\n{pformat(settings.dict())}")

    # Initialize logging
    init_logging(cli_settings.log)

    # Initialize database
    session_maker = await init_db(settings.db)

    # Initialize translator
    translator_hub = init_translator_hub()

    # Initialize bot, storage and dispatcher
    bot = Bot(token=settings.bot.token.get_secret_value(), parse_mode="html")
    storage = MemoryStorage()
    dp = Dispatcher(
        storage=storage,
        settings=settings,
        translator_hub=translator_hub,
    )

    # Register startup and shutdown handlers
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # Setup filter for private messages only
    dp.message.filter(F.chat.type == "private")

    # Setup routers
    await setup_routers(dp, settings)

    # Setup middlewares
    setup_middlewares(dp=dp, session_maker=session_maker)

    # Setup scheduler
    scheduler = setup_scheduler()

    # Set bot commands
    await set_commands(bot, settings)

    # Start bot
    try:
        if not cli_settings.webhook:
            logger.info("Start bot in polling mode")
            await bot.delete_webhook()
            await dp.start_polling(
                bot,
                skip_updates=True,
                allowed_updates=dp.resolve_used_update_types(),
                scheduler=scheduler,
            )

        else:
            logger.info("Start bot in webhook mode")
            await start_webhook(bot, dp, settings)

    finally:
        await bot.session.close()
        await dp.storage.close()
        await close_db()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped")
