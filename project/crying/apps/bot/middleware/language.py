from typing import Any

from aiogram.types import TelegramObject
from aiogram.utils.i18n import I18nMiddleware, I18n

from project.crying.config.config import I18N_DOMAIN, LOCALES_DIR


class LanguageMiddleware(I18nMiddleware):

    async def get_locale(self, event: TelegramObject, data: dict[str, Any]) -> str:
        user = data.get("user")
        return user.locale if user else "ru"


i18n = I18n(path=LOCALES_DIR, domain=I18N_DOMAIN)
_ = i18n.gettext
language_middleware = LanguageMiddleware(i18n)
