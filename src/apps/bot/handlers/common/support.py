from __future__ import annotations

from pprint import pformat

from aiogram import Router, types
from aiogram.filters import Command
from loguru import logger

from src.apps.bot.filters.support_connector import SupportConnectorFilter
from src.apps.bot.keyboards.common import common_kbs
from src.apps.bot.types.message import NonEmptyBotMessage
from src.utils.support import SupportConnector, SupportMessageInfo

on = Router(name=__name__)


@on.message(Command("support_buttons"))
async def support_buttons(msg: NonEmptyBotMessage):
    await msg.answer(
        "Выберите действие",
        reply_markup=common_kbs.thread_support(),
    )
    await msg.answer(
        "Выберите действие2",
        reply_markup=common_kbs.thread_support2(),
    )


@on.message(SupportConnectorFilter())
async def message(
    message: types.Message,
    support_connector: SupportConnector,
    support_message_info: SupportMessageInfo,
):
    smi = support_message_info
    try:
        if smi.close_thread and smi.to_user_id:
            return await support_connector.close_thread(smi.to_user_id)
        if smi.disconnect_user and smi.to_user_id:
            return await support_connector.disconnect_user(smi.to_user_id)
        if smi.to_user_id:
            return await support_connector.send_to_user(message, smi.to_user_id)
        if smi.to_thread_id:
            return await support_connector.send_to_thread(message, smi.to_thread_id)
    except Exception as e:
        logger.warning(
            f"Failed to send message to user {smi.to_user_id}: {e}. {pformat(message)}"
        )
        return None

    raise ValueError("to_user_id or to_thread_id is None")
