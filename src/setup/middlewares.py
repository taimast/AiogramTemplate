from aiogram import Dispatcher
from aiogram.utils.callback_answer import CallbackAnswerMiddleware
from loguru import logger
from sqlalchemy.ext.asyncio import async_sessionmaker

from ..apps.bot.middlewares import (
    UserMiddleware,
    TranslatorRunnerMiddleware,
    DBSessionMiddleware
)


def setup_middlewares(dp: Dispatcher, session_maker: async_sessionmaker):
    """
    Setup middlewares
    :param dp:
    :param session_maker:
    :return:
    """
    # Session maker middleware
    dp.update.middleware(DBSessionMiddleware(session_maker))

    # Get user middleware
    user_middleware = UserMiddleware()
    dp.message.middleware(user_middleware)
    dp.callback_query.middleware(user_middleware)

    # Translator middleware
    translator_runner_middleware = TranslatorRunnerMiddleware()
    dp.message.middleware(translator_runner_middleware)
    dp.callback_query.middleware(translator_runner_middleware)

    # Chat action middleware
    # chat_action_middleware = ChatActionMiddleware()
    # dp.message.middleware(chat_action_middleware)
    # dp.callback_query.middleware(chat_action_middleware)

    # edit = EditMessageMiddleware()
    # dp.message.middleware(edit)
    # dp.callback_query.middleware(edit)

    # Callback answer middleware
    dp.callback_query.middleware(CallbackAnswerMiddleware())

    logger.info("Middlewares setup completed")
