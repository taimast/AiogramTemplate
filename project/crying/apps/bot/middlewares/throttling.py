from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Update
from cachetools import TTLCache


class ThrottlingMiddleware(BaseMiddleware):
    # caches = {
    #     "spin": TTLCache(maxsize=10_000, ttl=THROTTLE_TIME_SPIN),
    #     "default": TTLCache(maxsize=10_000, ttl=THROTTLE_TIME_OTHER)
    # }
    # cache = TTLCache(maxsize=10_000, ttl=10)

    def __init__(self, ttl: float = 10) -> None:
        self.cache = TTLCache(maxsize=10_000, ttl=ttl)

    async def __call__(self,
                       handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
                       event: Update,
                       data: Dict[str, Any], ) -> Any:
        user = data.get('event_from_user')
        if user.id in self.cache:
            return
        return await handler(event, data)

        # throttling_key = get_flag(data, "throttling_key")
        # if throttling_key is not None and throttling_key in self.caches:
        #     if event.chat.id in self.caches[throttling_key]:
        #         return
        #     else:
        #         self.caches[throttling_key][event.chat.id] = None
        # return await handler(event, data)
