from __future__ import annotations

from typing import TYPE_CHECKING, Sequence, Callable

from aiogram import Router, types, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext

from src.apps.bot.callback_data.paginator import PaginatorCallback

if TYPE_CHECKING:
    from .....locales.stubs.ru.stub import TranslatorRunner

on = Router(name=__name__)

PgConsumer = Callable[[Sequence, PaginatorCallback], types.InlineKeyboardMarkup]
# PgProducer = Callable[[Sequence, PaginatorCallback], list[InputMedia]]
PgProducer = Callable[[Sequence, PaginatorCallback], str]


@on.callback_query(PaginatorCallback.filter())
# @flags.callback_answer(pre=True)
async def paginator(
        call: types.CallbackQuery,
        bot: Bot,
        callback_data: PaginatorCallback,
        l10n: TranslatorRunner,
        state: FSMContext
):
    data = await state.get_data()
    pg_data: Sequence = data.get("pg_data")
    pg_consumer: PgConsumer = data.get("pg_consumer")
    await state.update_data(pg=callback_data)
    try:
        await call.message.edit_reply_markup(
            reply_markup=pg_consumer(pg_data, callback_data)
        )
    except TelegramBadRequest as e:
        if "message is not modified" in e.message:
            await call.answer("Ничего не изменилось")
