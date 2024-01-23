from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Update
from cachetools import TTLCache


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, ttl: float = 10) -> None:
        self.cache: TTLCache[int, bool] = TTLCache(maxsize=10_000, ttl=ttl)

    async def __call__(self,
                       handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
                       event: Update,
                       data: Dict[str, Any], ) -> Any:
        user = data.get('event_from_user')
        if user.id in self.cache:
            return
        self.cache[user.id] = True
        return await handler(event, data)
