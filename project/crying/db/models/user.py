from __future__ import annotations

import datetime
import typing

from tortoise import fields

from project.crying.config import TIME_ZONE
from project.crying.db.models.base import AbstractUser

if typing.TYPE_CHECKING:
    from .subscription import Subscription


def get_chat_name(chat: User) -> str:
    if chat.first_name and chat.last_name:
        name = f"{chat.first_name} {chat.last_name}"
    elif chat.first_name:
        name = chat.first_name
    elif chat.last_name:
        name = chat.last_name
    elif chat.username:
        name = f"@{chat.username}"
    else:
        name = f"id{chat.id}"

    return f"{name} (@{chat.username})"


class User(AbstractUser):
    subscription: "Subscription"
    locale = fields.CharField(5, default="ru")

    @classmethod
    async def count_all(cls) -> int:
        return await cls.all().count()

    @classmethod
    async def count_new_today(cls) -> int:
        date = datetime.datetime.now(TIME_ZONE)
        return await User.filter(
            registered_at__year=date.year,
            registered_at__month=date.month,
            registered_at__day=date.day,
        ).count()
