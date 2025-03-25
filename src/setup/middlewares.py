from aiogram import Dispatcher
from aiogram.utils.callback_answer import CallbackAnswerMiddleware
from loguru import logger

from src.apps.bot.middlewares.edit_message import EditMessageMiddleware
from src.db.persistence_session.manager import PersistenceSessionManager

from ..apps.bot.middlewares import DBSessionMiddleware, TranslatorRunnerMiddleware
from ..apps.bot.middlewares.user.light import LightUserMiddleware


def setup_middlewares(
    dp: Dispatcher,
    session_manager: PersistenceSessionManager,
):
    """
    Setup middlewares
    :param dp:
    :param session_maker:
    :return:
    """
    # Session maker middleware
    db_session_middleware = DBSessionMiddleware(session_manager.db_sessionmaker)
    # dp.update.middleware(DBSessionMiddleware(session_manager.db_sessionmaker))
    dp.message.middleware(db_session_middleware)
    dp.callback_query.middleware(db_session_middleware)

    # # Get user middleware
    # user_middleware = RichUserMiddleware()
    # dp.message.middleware(user_middleware)
    # dp.callback_query.middleware(user_middleware)

    light_user_middleware = LightUserMiddleware(session_manager=session_manager)
    # TODO: [2025-02-25 01:27] taimast: тут хз, outer или inner middleware
    dp.message.outer_middleware(light_user_middleware)
    dp.callback_query.middleware(light_user_middleware)

    # Translator middleware
    translator_runner_middleware = TranslatorRunnerMiddleware()
    dp.message.middleware(translator_runner_middleware)
    dp.callback_query.middleware(translator_runner_middleware)

    # Chat action middleware
    # chat_action_middleware = ChatActionMiddleware()
    # dp.message.middleware(chat_action_middleware)
    # dp.callback_query.middleware(chat_action_middleware)

    edit = EditMessageMiddleware()
    dp.message.middleware(edit)
    dp.callback_query.middleware(edit)

    # Callback answer middleware
    dp.callback_query.middleware(CallbackAnswerMiddleware())

    logger.info("Middlewares setup completed")
