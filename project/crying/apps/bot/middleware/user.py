from typing import Callable, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.dispatcher.event.handler import CallableMixin
from aiogram.types import Message, CallbackQuery
from loguru import logger

from project.crying.db.models import User


class UserMiddleware(BaseMiddleware):

    async def __call__(
            self,
            handler: Callable[[Message | CallbackQuery, dict[str, Any]], Awaitable[Any]],
            event: Message | CallbackQuery,
            data: dict[str, Any]
    ) -> Any:

        logger.info(dir(handler))
        user = event.from_user
        logger.debug(f"Get user for User {user.id}")
        user, is_new = await User.get_or_create(
            id=user.id,
            defaults={
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "language": user.language_code,
            },
        )
        user_data = {"user": user, "is_new": False}
        if is_new:
            data.update(is_new=True)
            logger.info(f"Новый пользователь {user=}")

        data.update(user_data)
        return await handler(event, data)
