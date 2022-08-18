from aiogram import types
from aiogram.filters import BaseFilter
from loguru import logger

from project.crying.db.models import User


class UserFilter(BaseFilter):
    async def __call__(self, update: types.CallbackQuery | types.Message) -> dict[str, User]:
        user = update.from_user
        user, is_new = await User.get_or_create(
            user_id=user.id,
            defaults={
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "language": user.language_code,
            },
        )
        if is_new:
            logger.info(f"Новый пользователь {user=}")

        return {"user": user}
