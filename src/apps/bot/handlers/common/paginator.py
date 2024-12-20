from __future__ import annotations

import random
from typing import TYPE_CHECKING, Callable, Sequence

from aiogram import Bot, Router, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from loguru import logger

from src.apps.bot.callback_data.paginator import PaginatorCallback
from src.apps.bot.keyboards.common import common_kbs
from src.apps.bot.types.message import NonEmptyMessageCallbackQuery

if TYPE_CHECKING:
    from .....locales.stubs.ru.stub import TranslatorRunner

on = Router(name=__name__)

PgConsumer = Callable[[Sequence, PaginatorCallback], types.InlineKeyboardMarkup]
# PgProducer = Callable[[Sequence, PaginatorCallback], list[InputMedia]]
PgProducer = Callable[[Sequence, PaginatorCallback], str]


@on.message(Command("paginator_test"))
async def paginator_test(
    message: types.Message,
    l10n: TranslatorRunner,
    state: FSMContext,
):
    data = [str(i) for i in range(50)]
    random.shuffle(data)
    pg = PaginatorCallback(
        offset=0,
        limit=5,
    )
    await state.update_data(
        pg_data=data,
        pg_consumer=common_kbs.test_paginator,
    )
    await message.reply(
        text=", ".join(data[: pg.limit]),
        reply_markup=common_kbs.test_paginator(data, pg),
    )


@on.callback_query(PaginatorCallback.filter())
# @flags.callback_answer(pre=True)
async def paginator(
    call: NonEmptyMessageCallbackQuery,
    bot: Bot,
    callback_data: PaginatorCallback,
    l10n: TranslatorRunner,
    state: FSMContext,
):
    data = await state.get_data()
    pg_data: Sequence = data["pg_data"]
    pg_consumer: PgConsumer = data["pg_consumer"]
    if callback_data.sort_order:
        pg_data = callback_data.sort(pg_data, key=lambda x: x)
        await state.update_data(pg_data=pg_data)

    await state.update_data(pg=callback_data)
    logger.info(f"Paginator:\n{callback_data.model_dump()}")
    try:
        # await call.message.edit_reply_markup(
        #     reply_markup=pg_consumer(pg_data, callback_data)
        # )
        #
        consume_data = callback_data.slice(pg_data)
        await call.message.edit_text(
            text=", ".join(consume_data),
            reply_markup=pg_consumer(pg_data, callback_data),
        )

    except TelegramBadRequest as e:
        if "message is not modified" in e.message:
            await call.answer("Ничего не изменилось")
