from typing import Callable, Any, Awaitable

from aiogram import BaseMiddleware
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
        user = event.from_user
        logger.debug("Get user for User {}", user.id)
        is_new = False
        db_user = await User.get_or_none(id=user.id)
        if not db_user:
            logger.info(f"Новый пользователь {user=}")
            db_user = await User.create(**user.dict(exclude={"locale"}))
            is_new = True

        data.update(user=db_user, is_new=is_new)
        return await handler(event, data)
