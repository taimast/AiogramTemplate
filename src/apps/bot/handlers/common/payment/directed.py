from __future__ import annotations

import typing

from aiogram import Router, types, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from loguru import logger
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.bot.keyboards.common import payment_kbs
from src.apps.merchant import YooKassa
from src.apps.merchant.base import MerchantEnum
from src.config import Settings
from src.db.models import Invoice, User, Currency

on = Router()

if typing.TYPE_CHECKING:
    from src.locales.stubs.ru.stub import TranslatorRunner


class ExampleSub(BaseModel):
    title: str = 'Example Sub (5 day, 5$ )'
    duration: int = 5
    price: float = 5.0


@on.callback_query(StateFilter("payment-create"))
async def payment_merchant(
        call: types.CallbackQuery,
        session: AsyncSession,
        user: User,
        settings: Settings,
        l10n: TranslatorRunner,
        state: FSMContext
):
    merchant: MerchantEnum = MerchantEnum.YOOKASSA
    sub = ExampleSub()

    merchant: YooKassa = settings.get_merchant(merchant)
    currency = Currency.RUB
    invoice = await Invoice.get_last_invoice(
        session,
        user.id,
        sub.price,
        currency,
        merchant.merchant
    )
    if not invoice:
        invoice = await merchant.create_invoice(
            user.id,
            sub.price,
            currency=currency,
        )
        invoice.extra_data = sub.model_dump(mode="json")
        session.add(invoice)
        await session.commit()
    else:
        logger.info(f"Cached invoice: {invoice}")
    await call.message.answer(
        l10n.get("payment-created"),
        reply_markup=payment_kbs.payment_created(invoice.pay_url, l10n)
    )
    await state.clear()


@on.callback_query(F.data == "i_paid")
async def i_paid(
        call: types.CallbackQuery,
        l10n: TranslatorRunner,
):
    await call.message.answer(
        l10n.get("payment-i_paid")
    )
