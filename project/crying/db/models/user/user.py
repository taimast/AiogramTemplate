from __future__ import annotations

import datetime
from enum import StrEnum

from sqlalchemy import select, ForeignKey
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import mapped_column, Mapped, relationship

from .base import BaseUser
from ..base import Base


class Locale(StrEnum):
    """Language codes."""
    ENGLISH = 'en'
    RUSSIAN = 'ru'


class Private(Base):
    __tablename__ = 'privates'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped[User] = relationship(back_populates="private")


class User(BaseUser):
    __tablename__ = 'users'
    language_code: Mapped[Locale | None] = mapped_column(default=Locale.RUSSIAN)
    private: Mapped[Private] = relationship(back_populates="user")

    @classmethod
    async def today_count(cls, session: AsyncSession) -> int:
        result = await session.execute(
            select(cls).where(cls.created_at >= datetime.date.today()))
        return len(result.all())
