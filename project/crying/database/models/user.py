from __future__ import annotations

import typing
from enum import StrEnum

from sqlalchemy.orm import mapped_column, Mapped, relationship

from .base import AbstractUser

if typing.TYPE_CHECKING:
    from .invoice import AbstractInvoice


class Locale(StrEnum):
    """Language codes."""
    ENGLISH = 'en'
    RUSSIAN = 'ru'


class User(AbstractUser):
    __tablename__ = 'users'
    language_code: Mapped[Locale | None] = mapped_column(default=Locale.RUSSIAN)
    invoices: Mapped[list[AbstractInvoice]] = relationship(back_populates="user")
