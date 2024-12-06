from __future__ import annotations

from aiogram.filters import BaseFilter
from aiogram.types import Message

from src.utils.support import SupportConnector


class SupportConnectorFilter(BaseFilter):
    async def __call__(
        self,
        message: Message,
        support_connector: SupportConnector | None,
    ) -> bool | dict:
        sc = support_connector

        if sc:
            if (
                not message.forum_topic_created
                and message.message_thread_id
                and (message.chat.id == sc.chat_id)
            ):
                c_user_id = sc.get_user_id(message.message_thread_id)
                if c_user_id:
                    return {
                        "to_user_id": c_user_id,
                        "to_thread_id": None,
                    }

            elif message.from_user:
                c_thread_id = sc.get_thread_id(message.from_user.id)
                if c_thread_id:
                    return {
                        "to_user_id": None,
                        "to_thread_id": c_thread_id,
                    }

        return False
