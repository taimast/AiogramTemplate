from aiogram import Dispatcher
from aiogram.utils.callback_answer import CallbackAnswerMiddleware

from project.crying.apps.bot.middleware import UserMiddleware, TranslatorRunnerMiddleware


def setup_middlewares(dp: Dispatcher):
    # Мидлварь для получения пользователя
    user_middleware = UserMiddleware()
    dp.message.middleware(user_middleware)
    dp.callback_query.middleware(user_middleware)

    # Мидлварь для локализации
    translator_runner_middleware = TranslatorRunnerMiddleware()
    dp.message.middleware(translator_runner_middleware)
    dp.callback_query.middleware(translator_runner_middleware)

    # Мидлварь для обработки CallbackAnswer
    dp.callback_query.middleware(CallbackAnswerMiddleware())
