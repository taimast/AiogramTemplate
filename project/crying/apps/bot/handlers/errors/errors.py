import sys

from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types.error_event import ErrorEvent
from aiohttp import ContentTypeError
from loguru import logger

router = Router()


@router.errors()
async def error_handler(update: ErrorEvent):
    exception = update.exception
    if isinstance(exception, (TelegramBadRequest, ContentTypeError)):
        _type, _, tb = sys.exc_info()
        logger.opt(exception=(_type, None, tb)).error(exception.message)
        return True
    logger.exception(exception)
    return True
