import sys
from pprint import pprint
from typing import Any

from aiogram import Router, Bot
from aiogram.exceptions import DetailedAiogramError
from aiogram.handlers import ErrorHandler
from aiogram.types import User
from aiogram.types.error_event import ErrorEvent
from aiohttp import ContentTypeError
from loguru import logger

router = Router(name="error")


# @router.errors()
class MyHandler(ErrorHandler):
    event: ErrorEvent

    async def handle(self) -> Any:
        logger.exception(self.event.exception)



@router.errors()
async def error_handler(event: ErrorEvent, bot: Bot, event_from_user: User):
    await bot.send_message(event_from_user.id, "Произошла ошибка при обработке сообщения.\n"
                                               "Попробуйте еще раз или обратитесь к администратору.")
    exception = event.exception
    if isinstance(exception, (DetailedAiogramError, ContentTypeError)):
        _type, _, tb = sys.exc_info()
        logger.opt(exception=(_type, None, tb)).error(exception.message)
    else:
        logger.exception(exception)
