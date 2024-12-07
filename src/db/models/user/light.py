from __future__ import annotations

from typing import ClassVar, Self, Type

from src.apps.bot.types.user import TgUser
from src.db.models.base.light import LightBase
from src.db.models.user.user import Locale
from src.db.models.user.user import User as RichUser


class LightUser(LightBase[RichUser]):
    __key__: ClassVar[str] = "user"
    __rich_model__: ClassVar[Type[RichUser]] = RichUser
    id: int
    username: str | None = None
    language_code: str

    @classmethod
    def from_tg_user(cls, user: TgUser) -> Self:
        return cls(
            id=user.id,
            username=user.username,
            language_code=user.language_code or Locale.RUSSIAN,
        )
