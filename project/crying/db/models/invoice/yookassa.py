from loguru import logger
from tortoise import fields

from project.crying.config import config
from project.crying.config.merchant.yookassa import YooPayment
from project.crying.db.models import User
from project.crying.db.models.subscription import SubscriptionTemplate
from .base import AbstractInvoice


class InvoiceYooKassa(AbstractInvoice):
    """
        {'id': '2a60ca77-000f-5000-a000-16cf4119f15e', 'status': 'pending', 'amount': {'value': '1.00',
                                                                                       'currency': 'RUB'},
        'description': 'Текстовый', 'recipient': {'account_id': '878719', 'gateway_id': '1934486'},
        'created_at': '2022-07-13T12:12:39.501Z',
        'confirmation': {'type': 'redirect',
                         'confirmation_url': 'https://yoomoney.ru/checkout/payments/v2/contract?orderId=2a60ca77-000f-5000-a000-16cf4119f15e'},
        'test': False, 'paid': False, 'refundable': False, 'metadata': {}}
    """
    user: "User" = fields.ForeignKeyField("models.User", on_delete=fields.CASCADE, related_name="invoice_yookassas")
    comment = fields.CharField(255, null=True)

    async def check_payment(self) -> bool:
        return await config.merchants.yookassa.is_paid(self.invoice_id)

    @classmethod
    async def create_invoice(
            cls,
            user: "User",
            subscription_template: "SubscriptionTemplate",
            amount: int | float | str,
            comment: str = None,
            email: str = None,
            lifetime: int = 30,
    ) -> "InvoiceYooKassa":
        yoo_payment: YooPayment = await config.merchants.yookassa.create_invoice(
            amount=amount,
            description=comment,
        )
        logger.info(f"InvoiceYooKassa created [{user}][{yoo_payment.id}] {yoo_payment.confirmation.confirmation_url}")
        return await cls.create(
            user=user,
            subscription_template=subscription_template,
            amount=yoo_payment.amount.value,
            comment=comment,
            invoice_id=yoo_payment.id,
            pay_url=yoo_payment.confirmation.confirmation_url,
            email=email,
        )
