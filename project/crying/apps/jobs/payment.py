from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram import Bot
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from project.crying.apps.merchant import MerchantEnum
from project.crying.config import Settings
from project.crying.db.models import Invoice

if TYPE_CHECKING:
    from project.crying.locales.stubs.ru.stub import TranslatorRunner


# Payment verification job
async def payment_verification(
        session: AsyncSession,
        bot: Bot,
        settings: Settings,
        l10n: TranslatorRunner
):
    """Проверка оплаты."""
    logger.debug("Проверка оплаты")
    invoices = await Invoice.get_pending_invoices(session)
    for invoice in invoices:
        logger.trace("Check invoice {}", invoice)
        try:
            merchant = settings.get_merchant(invoice.merchant)
            if await merchant.is_paid(invoice.invoice_id):
                # if True:
                await invoice.successfully_paid(session, bot)

        except Exception as e:
            logger.exception(e)
