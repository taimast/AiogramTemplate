from __future__ import annotations

from pprint import pformat

from aiogram import Router, types
from loguru import logger

from src.apps.bot.filters.support_connector import SupportConnectorFilter
from src.utils.support import SupportConnector

on = Router(name=__name__)


@on.message(SupportConnectorFilter())
async def message(
    message: types.Message,
    support_connector: SupportConnector,
    to_user_id: int | None,
    to_thread_id: int | None,
):
    try:
        if to_user_id:
            return await support_connector.send_to_user(message, to_user_id)
        if to_thread_id:
            return await support_connector.send_to_thread(message, to_thread_id)
    except Exception as e:
        logger.warning(f"Failed to send message to user {to_user_id}: {e}. {pformat(message)}")
        return None

    raise ValueError("to_user_id or to_thread_id is None")
