from enum import StrEnum

from sqlalchemy import BigInteger
from sqlalchemy.orm import mapped_column, Mapped

from .base import Base


class Locale(StrEnum):
    """Language codes."""
    ENGLISH = 'en'
    RUSSIAN = 'ru'


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    locale: Mapped[Locale] = mapped_column(default=Locale.RUSSIAN)
