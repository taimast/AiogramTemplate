import datetime

from loguru import logger
from project.crying.apps.account.controller import start_controller
from project.crying.apps.bot.temp import controllers

from project.crying.config.config import TIME_ZONE
from project.crying.db.models import Account
from project.crying.db.models.invoice.crypto_cloud import InvoiceCrypto
from project.crying.db.models.invoice.qiwi import InvoiceQiwi
from project.crying.db.models.invoice.yookassa import InvoiceYooKassa

_ = lambda x: x


async def checking_purchases():
    logger.trace("Checking purchases")
    try:
        for cls in [InvoiceCrypto, InvoiceQiwi, InvoiceYooKassa]:
            logger.trace(f"Check cls {cls.__name__}")
            invoices: list[InvoiceCrypto, InvoiceQiwi, InvoiceYooKassa] = await cls.filter(
                expire_at__gte=datetime.datetime.now(TIME_ZONE),
                is_paid=False)
            for invoice in invoices:
                logger.trace(f"Check invoice {invoice.invoice_id}[{invoice.amount}]")
                try:
                    if await invoice.check_payment():
                        await invoice.successfully_paid()
                        logger.success(
                            f"The invoice [{cls.__name__}] [{invoice.user}]{invoice.amount} {invoice.currency} "
                            f"has been successfully paid")

                        await bot.send_message(invoice.user.id,
                                               _("✅ Подписка {} успешно оплачена").format(
                                                   invoice.subscription_template))

                        user = invoice.user
                        for account in await Account.filter(owner=user).prefetch_related(
                                "owner__subscription", "trigger_collection__triggers",
                                "trigger_collection__account"):
                            if not controllers.get(account.trigger_collection.pk):
                                await start_controller(account)

                except Exception as e:
                    logger.warning(e)
    except Exception as e:
        logger.error(e)
