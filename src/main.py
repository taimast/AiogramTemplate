import asyncio
from pprint import pformat

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.strategy import FSMStrategy
from loguru import logger

from src import setup
from src.config import Settings
from src.setup.cli import Mode
from src.setup.opts import SetupOpts
from src.setup.webadmin import setup_webadmin
from src.utils.other import send_start_info
from src.utils.support import SupportConnector


async def on_startup(settings: Settings, bot: Bot):
    _task = asyncio.create_task(send_start_info(settings, bot, only_text=True))


async def on_shutdown(bot: Bot):
    pass


async def main():
    # Parse command line arguments
    cli_settings = setup.parse_args()
    cli_settings.update_settings(Settings)

    # Initialize logging
    setup.init_logging(cli_settings.log)

    # Initialize settings
    settings = Settings()  # type: ignore
    logger.info(f"Settings:\n{pformat(settings.model_dump())}")

    # Initialize database
    session_maker = await setup.init_db(settings.db, echo=cli_settings.mode == Mode.DEV)

    # Initialize translator
    translator_hub = setup.init_translator_hub()

    # Initialize bot, storage and dispatcher
    bot = Bot(
        token=settings.bot.token.get_secret_value(),
        default=DefaultBotProperties(parse_mode="html"),
        session=AiohttpSession(proxy=settings.bot.proxy),
    )

    # Setup scheduler
    scheduler = await setup.setup_scheduler()

    base_l10n = translator_hub.get_translator_by_locale("ru")

    # Setup options
    opts = SetupOpts(
        session_maker=session_maker,
        bot=bot,
        settings=settings,
        l10n=base_l10n,
    )

    # Setup session manager
    session_manager = await setup.setup_session_manager(opts)

    if settings.support:
        support_connector = SupportConnector(bot, settings.support.chat_id)
    else:
        support_connector = None

    storage = MemoryStorage()
    dp = Dispatcher(
        storage=storage,
        settings=settings,
        session_manager=session_manager,
        support_connector=support_connector,
        translator_hub=translator_hub,
        scheduler=scheduler,
        fsm_strategy=FSMStrategy.GLOBAL_USER,
    )
    # Register startup and shutdown handlers
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # TODO: #TEST-21:30min Puzzle description
    await setup.setup_routers(dp, settings)

    # Setup middlewares
    setup.setup_middlewares(dp, session_manager)

    # Set bot commands
    await setup.set_commands(bot, settings)

    # setup web admin
    if settings.webadmin:
        await setup_webadmin(opts)

    # Start bot
    try:
        if not cli_settings.webhook:
            logger.info("Start bot in polling mode")
            await bot.delete_webhook()
            await dp.start_polling(
                bot,
                skip_updates=True,
                allowed_updates=dp.resolve_used_update_types(),
            )

        elif settings.webhook:
            logger.info("Start bot in webhook mode")
            await setup.start_webhook(bot, dp, settings.webhook)
        else:
            raise ValueError("Cli webhook is True, but settings.webhook is False")

    finally:
        await bot.session.close()
        await dp.storage.close()
        await setup.close_db()


def start_runner():
    try:
        import uvloop  # type: ignore

        with asyncio.Runner(loop_factory=uvloop.new_event_loop) as runner:
            runner.run(main())
    except ImportError:
        logger.warning("uvloop is not installed")
        asyncio.run(main())


if __name__ == "__main__":
    try:
        start_runner()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped")
