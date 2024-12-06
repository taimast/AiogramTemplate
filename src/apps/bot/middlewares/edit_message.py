from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message


class EditMessageMiddleware(BaseMiddleware):
    async def __call__(  # type: ignore
        self,
        handler: Callable[[Message | CallbackQuery, dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: dict[str, Any],
    ) -> Any:
        if isinstance(event, Message):
            data["edit"] = event.answer
            data["orig_msg"] = event
        elif isinstance(event, CallbackQuery):
            if isinstance(event.message, Message):
                if getattr(event.message, "text", None):
                    data["edit"] = event.message.edit_text
                else:
                    data["edit"] = event.message.answer
                data["orig_msg"] = event.message
        return await handler(event, data)
