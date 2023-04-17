from enum import StrEnum

from sqlalchemy.orm import mapped_column, Mapped

from .base import AbstractUser


class Locale(StrEnum):
    """Language codes."""
    ENGLISH = 'en'
    RUSSIAN = 'ru'


class User(AbstractUser):
    __tablename__ = 'users'
    language_code: Mapped[Locale | None] = mapped_column(default=Locale.RUSSIAN)
