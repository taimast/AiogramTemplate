from typing import Callable, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery


class EditMessageMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message | CallbackQuery, dict[str, Any]], Awaitable[Any]],
            event: Message | CallbackQuery,
            data: dict[str, Any]
    ) -> Any:
        if isinstance(event, Message):
            data["edit"] = event.answer
        elif isinstance(event, CallbackQuery):
            data["edit"] = event.message.edit_text
        return await handler(event, data)
