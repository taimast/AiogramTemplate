from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message
from fluentogram import TranslatorHub

from src.db.models import User


# todo L1 TODO 01.03.2023 15:17 taima: Может замедлиться из-за доступа по атрибутам

class TranslatorRunnerMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        hub: TranslatorHub = data.get('translator_hub')
        user: User = data.get('user')
        # There you can ask your database for locale
        data['l10n'] = hub.get_translator_by_locale(user.language_code)
        return await handler(event, data)
