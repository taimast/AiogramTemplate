import sys

from aiogram import Dispatcher, Router
from aiogram.exceptions import TelegramBadRequest
from loguru import logger

router = Router()


async def error_handler(update, exception: TelegramBadRequest):
    if isinstance(exception, TelegramBadRequest):
        _type, _, tb = sys.exc_info()
        logger.opt(exception=(_type, None, tb)).error("An error occurred")
        return True
    logger.exception(exception)
    return True


def register_error(dp: Dispatcher):
    dp.include_router(router)
    router.errors.register(error_handler)
