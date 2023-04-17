from typing import Protocol, TypeVar

from aiogram.types import TelegramObject
from aiogram.utils.i18n import I18nMiddleware

from ....db.models import User


class HasLocale(Protocol):
    locale: str


T = TypeVar("T")


class LanguageMiddleware(I18nMiddleware):

    async def get_locale(self, event: TelegramObject, data: dict[str, User]) -> str:
        user = data.get("user")
        user: HasLocale
        return user.locale if user else "ru"

# i18n = I18n(path=LOCALES_DIR, domain=I18N_DOMAIN)
# language_middleware = LanguageMiddleware(i18n)
# _ = i18n.gettext
# __ = i18n.lazy_gettext
