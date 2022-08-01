from typing import Callable, Any, Awaitable

from aiogram import BaseMiddleware, types
from aiogram.types import CallbackQuery, Update
from loguru import logger

from project.crying.config.config import config
from project.crying.db.models import User


async def get_user(update: types.CallbackQuery | types.Message) -> dict[str, User] | bool:
    user = update.from_user
    logger.debug(f"Get user for User {user.id}")
    user, is_new = await User.get_or_create(
        user_id=user.id,
        defaults={
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "language": user.language_code,
        },
    )
    data = {"user": user, "is_new": False}
    if is_new:
        data.update(is_new=True)
        logger.info(f"Новый пользователь {user=}")
    return data


class BotMiddleware(BaseMiddleware):

    async def __call__(
            self,
            handler: Callable[[Update | CallbackQuery, dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: dict[str, Any]
    ) -> Any:
        if data.get('bot_running') or (data.get('event_from_user').id in config.bot.admins):
            return await handler(event, data)
