from typing import Self

from loguru import logger
from tortoise import fields

from project.crying.config.merchant.yookassa import YooPayment, YooKassa
from .base import AbstractInvoice
from ..subscription import SubscriptionTemplate
from ..user import User


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

    async def check_payment(self, merchant: YooKassa) -> bool:
        return await merchant.is_paid(self.invoice_id)

    @classmethod
    async def create_invoice(
            cls,
            merchant: YooKassa,
            user: "User",
            subscription_template: "SubscriptionTemplate",
            amount: int | float | str,
            comment: str = None,
            email: str = None,
    ) -> Self:
        yoo_payment: YooPayment = await merchant.create_invoice(
            amount=amount,
            description=comment,
        )

        created_invoice = await cls.create(
            amount=yoo_payment.amount.value,
            currency=yoo_payment.amount.currency,
            invoice_id=yoo_payment.id,
            pay_url=yoo_payment.confirmation.confirmation_url,

            user=user,
            subscription_template=subscription_template,
            comment=comment,
            email=email,
        )
        logger.info(f"InvoiceYooKassa created [{user.id}][{created_invoice.invoice_id}] {created_invoice.pay_url}")
        return created_invoice
