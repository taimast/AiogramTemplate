from __future__ import annotations

import datetime
import typing

from tortoise import fields
from tortoise.transactions import atomic

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


class User(AbstractUser):
    subscription: "Subscription"
    locale = fields.CharField(5, default="ru")
    is_connected = fields.BooleanField(default=False)
    connected_user: User | None = fields.OneToOneField(
        "models.User",
        related_name="reverse_connected_user",
        null=True
    )
    reverse_connected_user: fields.OneToOneNullableRelation[User]

    @property
    def name(self):
        return get_chat_name(self)

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

    @atomic()
    async def connect(self, user: "User", reverse: bool = True) -> None:
        self.is_connected = True
        self.connected_user = user
        await self.save(update_fields=["is_connected", "connected_user_id"])
        if reverse:
            await user.connect(self, reverse=False)

    @atomic()
    async def disconnect(self, reverse: bool = True) -> None:
        self.is_connected = False
        connected_user = self.connected_user
        self.connected_user = None
        await self.save(update_fields=["is_connected", "connected_user_id"])
        if reverse and connected_user:
            await connected_user.disconnect(reverse=False)
