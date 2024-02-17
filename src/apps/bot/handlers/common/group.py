from __future__ import annotations

from aiogram import Router, types, Bot, F
from aiogram.filters import ChatMemberUpdatedFilter, ADMINISTRATOR
from aiogram.fsm.context import FSMContext
from loguru import logger

from src.apps.bot.keyboards.common import common_kbs
from src.config import Settings

on = Router(name=__name__)


@on.my_chat_member(ChatMemberUpdatedFilter(ADMINISTRATOR))
async def my_chat_member(update: types.Message, bot: Bot, settings: Settings):
    logger.info(f"Chat id: {update.chat.id} saved")


@on.chat_join_request()
async def join_request(update: types.ChatJoinRequest, bot: Bot, settings: Settings, state: FSMContext):
    logger.info(f"Join request from {update.from_user.full_name}")
    await state.update_data(join_request=update)
    await update.bot.send_message(
        update.from_user.id,
        "you want join?",
        reply_markup=common_kbs.want_join()
    )
    await update.approve()


@on.callback_query(F.data == "yes")
async def yes(update: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    join_request: types.ChatJoinRequest = data.get("join_request")
    await join_request.approve()
    await update.message.answer("accepted")
