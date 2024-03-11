from __future__ import annotations

import datetime
from typing import Optional, Literal

try:
    from glQiwiApi import QiwiP2PClient
except ImportError:
    QiwiP2PClient = None

from pydantic import validator

from .base import PAYMENT_LIFETIME, TIME_ZONE, BaseMerchant, MerchantEnum
import typing

if typing.TYPE_CHECKING:
    from ...db.models import Invoice


# todo L1 24.11.2022 18:29 taima: Использовать кастомную платежную систему вместо модуля glQiwiApi
#  Каждый раз открывается и закрывается сессия, что не есть хорошо
class Qiwi(BaseMerchant):
    client: Optional[QiwiP2PClient]
    merchant: Literal[MerchantEnum.QIWI]

    class Config:
        arbitrary_types_allowed = True

    @validator("client", always=True)
    def client_validator(cls, v, values):
        if not v:
            api_key = values.get("api_key")
            v = QiwiP2PClient(secret_p2p=api_key.get_secret_value())
        return v

    async def create_invoice(
            self,
            user_id: int,
            amount: int | float | str,
            description: str = None,
            email: str = None,
    ) -> Invoice:
        from ...db.models import Invoice
        bill = await self.client.create_p2p_bill(
            amount=amount,
            comment=description or f"Product {amount}",
            expire_at=datetime.datetime.now(TIME_ZONE) + datetime.timedelta(seconds=PAYMENT_LIFETIME),
        )
        return Invoice(
            user_id=user_id,
            amount=bill.amount.value,
            currency=bill.amount.currency,
            invoice_id=bill.id,
            pay_url=bill.pay_url,
            email=email,
            description=description,
            merchant=self.merchant,
        )

    async def is_paid(self, invoice_id: str) -> bool:
        return (await self.client.get_bill_status(invoice_id)) == "PAID"
