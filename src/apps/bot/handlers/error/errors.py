import sys

from aiogram import Bot, Router
from aiogram.exceptions import DetailedAiogramError
from aiogram.types import User
from aiogram.types.error_event import ErrorEvent
from aiohttp import ContentTypeError
from loguru import logger

on = Router(name=__name__)


@on.errors()
async def error_handler(event: ErrorEvent, bot: Bot, event_from_user: User):
    # text = ("Произошла ошибка при обработке сообщения.\n"
    #         "Попробуйте еще раз или обратитесь к администратору.\n"
    #         "Сообщение об ошибке:\n"
    #         "{}".format(event.exception))
    exception = event.exception
    if isinstance(exception, (DetailedAiogramError, ContentTypeError)):
        _type, _, tb = sys.exc_info()
        logger.opt(exception=(_type, None, tb)).error(exception.message)
    else:
        logger.exception(exception)
    # await bot.send_message(event_from_user.id, text, parse_mode=None)
