from __future__ import annotations

from aiogram.filters import BaseFilter
from aiogram.types import Message
from loguru import logger

from src.utils.support import SupportConnector


class SupportConnectorFilter(BaseFilter):
    async def __call__(
        self,
        message: Message,
        support_connector: SupportConnector | None,
    ) -> bool | dict:
        sc = support_connector

        if sc:
            support_message_info = sc.get_message_info(message)
            logger.info(f"Support message info: {support_message_info}")
            if support_message_info and not support_message_info.is_disconnected_user:
                return {"support_message_info": support_message_info}
        return False
