from _pydecimal import Decimal
from typing import Self

from tortoise import fields
from tortoise.transactions import atomic

from .base import AbstractInvoice
from ..user import User
from ....apps.merchant.usdt import USDT


class USDTInvoice(AbstractInvoice):
    currency = fields.CharField(5, default="USDT", description="USDT")
    amount = fields.DecimalField(16, 5)
    pay_url = fields.CharField(255, null=True)
    invoice_id = fields.IntField(index=True)

    @atomic()
    async def successfully_paid(self):
        await self.fetch_related("user")
        await self.user.add_balance(self.amount)
        self.is_paid = True
        await self.save(update_fields=["is_paid"])

    async def check_payment(self, merchant: USDT) -> bool:
        return await merchant.is_paid(self.amount)

    @classmethod
    async def get_next_invoice_id(cls) -> int:
        """Получение следующего самого минимального invoice_id"""
        exists_values = await cls.all().order_by(
            "-invoice_id"
        ).limit(100).values_list("invoice_id", flat=True)
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
            merchant: USDT,
            user: User,
            amount: int | float | str,
            currency="USDT",
            order_id: str = None,
    ) -> Self:
        invoice_id = await cls.get_next_invoice_id()
        amount = cls.create_amount(amount, invoice_id)
        created_invoice = await cls.create(
            amount=amount,
            currency=currency,
            invoice_id=invoice_id,
            user=user,
        )
        return created_invoice
