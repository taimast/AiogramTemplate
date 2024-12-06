from __future__ import annotations

from typing import ClassVar, Self, Type, TypeVar

from aiogram.types import User as TgUser
from pydantic import BaseModel
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import async_session, async_sessionmaker

from src.db.models.base.light import LightBase, PersistenceSessionManager
from src.db.models.user.user import Locale
from src.db.models.user.user import User as RichUser


class LightUser(LightBase["LightUser", RichUser]):
    __key__: ClassVar[str] = "user"
    __rich_model__: ClassVar[Type[RichUser]] = RichUser
    id: int
    username: str | None = None
    language_code: str
