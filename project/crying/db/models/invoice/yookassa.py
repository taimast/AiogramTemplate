from typing import Self

from loguru import logger
from sqlalchemy import String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import mapped_column, Mapped

from .base import AbstractInvoice
from ..user import User
from ....apps.merchant.yookassa import YooPayment, YooKassa


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
    __tablename__ = "invoice_yookassa"
    comment: Mapped[str | None] = mapped_column(String(255))

    @classmethod
    async def create_invoice(
            cls,
            session: AsyncSession,
            merchant: YooKassa,
            user: "User",
            amount: int | float | str,
            comment: str = None,
            email: str = None,
    ) -> Self:
        yoo_payment: YooPayment = await merchant.create_invoice(
            amount=amount,
            description=comment,
        )

        created_invoice = await cls.create(
            session=session,
            user=user,
            amount=yoo_payment.amount.value,
            currency=yoo_payment.amount.currency,
            invoice_id=yoo_payment.id,
            pay_url=yoo_payment.confirmation.confirmation_url,
            comment=comment,
            email=email,
        )
        logger.info(f"InvoiceYooKassa created [{user.id}][{created_invoice.invoice_id}] {created_invoice.pay_url}")
        return created_invoice
