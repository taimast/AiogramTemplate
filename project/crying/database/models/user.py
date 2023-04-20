from __future__ import annotations

import typing
from enum import StrEnum

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import mapped_column, Mapped

from .base import AbstractUser

if typing.TYPE_CHECKING:
    pass


class Locale(StrEnum):
    """Language codes."""
    ENGLISH = 'en'
    RUSSIAN = 'ru'


class User(AbstractUser):
    __tablename__ = 'users'
    language_code: Mapped[Locale | None] = mapped_column(default=Locale.RUSSIAN)
    locked: Mapped[bool] = mapped_column(default=False)

    # invoices: Mapped[list[AbstractInvoice]] = relationship(back_populates="user")

    async def __aenter__(self):
        self.locked = True
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.locked = False

    @classmethod
    async def today_count(cls, session: AsyncSession) -> int:
        result = await session.execute(
            select(cls).where(cls.created_at >= datetime.date.today()))
        return len(result.all())
