from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Update
from aiogram.types import User as TgUser
from cachetools import TTLCache


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, ttl: float = 10) -> None:
        self.cache: TTLCache[int, bool] = TTLCache(maxsize=10_000, ttl=ttl)

    async def __call__(  # type: ignore
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:
        user: TgUser = data["event_from_user"]
        user.mention_html
        if user.id in self.cache:
            return None
        self.cache[user.id] = True
        return await handler(event, data)
