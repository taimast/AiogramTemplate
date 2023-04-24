from _pydecimal import Decimal
from typing import Self

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .base import AbstractInvoice, Currency
from ..user import User
from ....apps.merchant.usdt import USDT


class USDTInvoice(AbstractInvoice):
    __tablename__ = "invoice_usdt"
    @classmethod
    async def get_next_invoice_id(cls, session: AsyncSession) -> int:
        """Получение следующего самого минимального invoice_id"""
        exists_values = (await session.execute(
            select(cls.invoice_id).order_by(cls.invoice_id.desc()).limit(100)
        )).scalars().all()

        if not exists_values:
            return 1
        for i in range(1, max(exists_values) + 2):
            if i not in exists_values:
                return i

    @classmethod
    def create_amount(cls, amount: int | float | str, invoice_id: int) -> str:
        """Adding invoice_id to the end of amount. Max decimal places is 5.

        Example:
            >>> assert USDTInvoice.create_amount(1, 1) == "1.00001"
            >>> assert USDTInvoice.create_amount(1.1, 1) == "1.10001"
            >>> assert USDTInvoice.create_amount(1.123, 1) == "1.12301"
            >>> assert USDTInvoice.create_amount(1.12345, 1) == "1.12345"
        """

        # Convert the amount to a float with a maximum of 5 decimal places
        decimal_places = 5
        amount = Decimal(str(amount))
        invoice_id = Decimal(str(invoice_id))
        result = amount + invoice_id / 10 ** decimal_places
        return f"{result:.{decimal_places}f}"

    @classmethod
    async def create_invoice(
            cls,
            session: AsyncSession,
            merchant: USDT,
            user: User,
            amount: int | float | str,
            currency: Currency = Currency.USDT,
    ) -> Self:
        invoice_id = await cls.get_next_invoice_id(session)
        amount = cls.create_amount(amount, invoice_id)
        created_invoice = await cls.create(
            session=session,
            user=user,
            amount=amount,
            currency=currency,
            invoice_id=invoice_id,
        )
        return created_invoice
