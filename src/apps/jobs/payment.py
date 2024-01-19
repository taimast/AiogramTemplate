from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram import Bot
from loguru import logger
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.config import Settings
from src.db.models import Invoice

if TYPE_CHECKING:
    from src.locales.stubs.ru.stub import TranslatorRunner


# Payment verification job
async def payment_verification(
        session_maker: async_sessionmaker,
        bot: Bot,
        settings: Settings,
        l10n: TranslatorRunner
):
    """Проверка оплаты."""
    logger.debug("Проверка оплаты")
    async with session_maker() as session:
        invoices = await Invoice.get_pending_invoices(session)
        for invoice in invoices:
            logger.trace("Check invoice {}", invoice)
            try:
                merchant = settings.get_merchant(invoice.merchant)
                if await merchant.is_paid(invoice.invoice_id):
                    # if True:
                    await invoice.successfully_paid()

            except Exception as e:
                logger.exception(e)
