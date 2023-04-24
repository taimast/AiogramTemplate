from typing import Self

from loguru import logger
from sqlalchemy import String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from project.crying.apps.merchant.crypto_cloud import CryptoCloud
from .base import AbstractInvoice, Currency
from ..user import User


class InvoiceCrypto(AbstractInvoice[CryptoCloud]):
    """
    for create:
        amount
        shop_id
        order_id
        email
        currency

    result:
        {'status': 'success',
        'pay_url': 'https://cryptocloud.plus/pay/4N8RWT',
        'currency': 'BTC',
        'invoice_id': '4N8RWT',
        'amount': 3e-06,
        'amount_usd': 0.1170788818966779}
    check result:
        {'status': 'success', 'status_invoice': 'created'}
        {'status': 'success', 'status_invoice': 'paid'}
    checked time:
        7-10 m
    """
    __tablename__ = "invoice_crypto"
    order_id: Mapped[str | None] = mapped_column(String(50), index=True, doc="Custom product ID")
    email: Mapped[str | None] = mapped_column(String(50), index=True, doc="Customer email")

    @classmethod
    async def create_invoice(
            cls,
            session: AsyncSession,
            merchant: CryptoCloud,
            user: User,
            amount: int | float | str,
            currency: Currency.RUB = Currency.RUB,
            email: str = None,
            order_id: str = None,
    ) -> Self:
        crypto_payment = await merchant.create_invoice(
            amount=amount,
            currency=currency,
            order_id=order_id,
            email=email,
        )

        created_invoice = await cls.create(
            session=session,
            user=user,
            amount=amount,
            currency=currency,
            invoice_id=crypto_payment.invoice_id,
            pay_url=crypto_payment.pay_url,
            order_id=order_id,
            email=email,
        )

        logger.info(f"InvoiceCrypto created [{user.id}][{created_invoice.invoice_id}] {created_invoice.pay_url}")
        return created_invoice
