import asyncio

from aiogram import Bot, F, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from loguru import logger

from project.crying.config.cli import CLIArgsSettings
from project.crying.config.config import Settings
from project.crying.config.logg_settings import init_logging, Level
from project.crying.db import init_db, close_db
from project.crying.setup import setup_routers, setup_middlewares, set_commands, start_scheduler, start_webhook, \
    init_translator_hub


# todo L1 TODO 18.02.2023 6:36 taima: Скопировать все из autoanswer
# todo L1 TODO 18.02.2023 7:06 taima: Сделать ввиде раздельных импортируемых модулей
# todo L1 TODO 18.02.2023 7:07 taima: Включить aiogram_admin в проект
async def main():
    # Парсинг аргументов командной строки
    cli_settings = CLIArgsSettings.parse_args()
    cli_settings.update_settings(Settings)
    cli_settings.log.stdout = Level.TRACE
    # cli_settings.log.file = Level.TRACE

    # Инициализация настроек
    settings = Settings()

    # Инициализация логирования
    init_logging(cli_settings.log)

    # Инициализация базы данных
    await init_db(settings.db)

    # Инициализация переводчика
    translator_hub = init_translator_hub()

    # Инициализация бота
    bot = Bot(token=settings.bot.token.get_secret_value(), parse_mode="html")
    storage = MemoryStorage()
    dp = Dispatcher(
        storage=storage,
        settings=settings,
        translator_hub=translator_hub,
    )

    # Настройка фильтра только для приватных сообщений
    dp.message.filter(F.chat.type == "private")

    # Настройка роутеров обработчиков
    await setup_routers(dp, settings)

    # Настройка мидлварей
    setup_middlewares(dp)

    # Запуск планировщика
    start_scheduler()

    # Установка команд бота
    await set_commands(bot, settings)

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
    asyncio.run(main())
