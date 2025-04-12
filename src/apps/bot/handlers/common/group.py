from __future__ import annotations

from pprint import pprint

from aiogram import Bot, F, Router, types
from loguru import logger

from src.apps.bot.keyboards.common import helper_kbs

on = Router(name=__name__)
on.message.filter(F.chat.type != "private")


@on.chat_member()
async def chat_member(update: types.ChatMemberUpdated, bot: Bot):
    logger.debug("chat_member")


@on.my_chat_member()
async def my_chat_member(update: types.ChatMemberUpdated, bot: Bot):
    logger.debug("my_chat_member")


@on.callback_query(F.data == "some_data")
async def process_callback_query(call: types.CallbackQuery, bot: Bot):
    logger.debug("process_callback_query")
    await bot.send_message(call.message.chat.id, "process_callback_query")


@on.message(F.text == "/get_data_button")
async def get_data_button(update: types.Message, bot: Bot):
    logger.debug("get_data_button")
    await bot.send_message(
        update.chat.id,
        "get_data_button",
        reply_markup=helper_kbs.custom_back_kb(cd="some_data"),
    )


@on.channel_post(F.text == "/get_data_button")
async def get_data_button2(update: types.Message, bot: Bot):
    logger.debug("get_data_button")
    await bot.send_message(
        update.chat.id,
        "get_data_button",
        reply_markup=helper_kbs.custom_back_kb(cd="some_data"),
    )


# @on.message()
# async def message(
#     update: types.Message,
#     bot: Bot,
# ):
#     pprint(update.model_dump())
