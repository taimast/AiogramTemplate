from __future__ import annotations

import datetime
import typing
from enum import StrEnum

from tortoise import fields

from .base import AbstractUser
from ...config import TIME_ZONE

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


class Locale(StrEnum):
    """Language codes."""
    ENGLISH = 'en'
    RUSSIAN = 'ru'


class User(AbstractUser):
    subscription: "Subscription"
    locale = fields.CharEnumField(Locale, max_length=2, default=Locale.RUSSIAN)

    @classmethod
    async def count_all(cls) -> int:
        return await cls.all().count()

    @classmethod
    async def count_new_today(cls) -> int:
        return await cls.filter(registered_at__gte=datetime.datetime.now(tz=TIME_ZONE).date()).count()

    @classmethod
    async def today_count(cls) -> int:
        return await cls.filter(registered_at__gte=datetime.datetime.now(tz=TIME_ZONE).date()).count()
