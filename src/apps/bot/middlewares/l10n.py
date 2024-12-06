from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message
from fluentogram import TranslatorHub

from src.db.models.user.light import LightUser

# todo L1 TODO 01.03.2023 15:17 taima: Может замедлиться из-за доступа по атрибутам


class TranslatorRunnerMiddleware(BaseMiddleware):
    async def __call__(  # type: ignore
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        hub: TranslatorHub = data["translator_hub"]
        user: LightUser = data["light_user"]
        data["l10n"] = hub.get_translator_by_locale(user.language_code)
        return await handler(event, data)
