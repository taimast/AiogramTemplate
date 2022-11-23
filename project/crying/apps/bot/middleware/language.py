from typing import Any, Protocol, TypeVar

from aiogram.types import TelegramObject
from aiogram.utils.i18n import I18nMiddleware, I18n

from project.crying.config.config import I18N_DOMAIN, LOCALES_DIR
from project.crying.db.models import User


class HasLocale(Protocol):
    locale: str


T = TypeVar("T")


class LanguageMiddleware(I18nMiddleware):

    async def get_locale(self, event: TelegramObject, data: dict[str, User]) -> str:
        user = data.get("user")
        user: HasLocale
        return user.locale if user else "ru"


i18n = I18n(path=LOCALES_DIR, domain=I18N_DOMAIN)
language_middleware = LanguageMiddleware(i18n)
_ = i18n.gettext
__ = i18n.lazy_gettext
