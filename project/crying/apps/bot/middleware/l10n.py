from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message
from fluent.runtime import FluentResourceLoader, FluentLocalization as _FluentLocalization
from project.crying.db.models import User



class FluentLocalization(_FluentLocalization):

    def __call__(self, msg_id, args=None):
        return self.format_value(msg_id, args)


class L10nMiddleware(BaseMiddleware):
    # # todo L1 26.11.2022 17:10 taima: Добавить несколько языков
    def __init__(
            self,
            loader: FluentResourceLoader,
            default_locale: str,
            locales: list[str],
            resource_ids: list[str]
    ):
        self.locales: dict[str, FluentLocalization] = {
            default_locale: FluentLocalization([default_locale], resource_ids, loader)
        }
        for locale in locales:
            self.locales[locale] = FluentLocalization(
                [default_locale, locale], resource_ids, loader
            )

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        user: User = data["user"]
        locale = user.locale
        if locale not in self.locales:
            locale = "ru"
        data["l10n"] = self.locales[locale]
        await handler(event, data)
