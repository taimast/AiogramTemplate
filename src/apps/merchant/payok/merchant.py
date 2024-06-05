from __future__ import annotations

import datetime
import typing
import uuid
from typing import Optional, Literal

from pydantic import validator, field_serializer
from pypayment import PaymentStatus

from src.apps.merchant.base import BaseMerchant, MerchantEnum, PAYMENT_LIFETIME
from src.apps.merchant.betatransfer.methods import BTPaymentTypeRUB
from src.apps.merchant.payok.aiopayok import Payok

if typing.TYPE_CHECKING:
    from src.db.models.invoice import Invoice


class PayokPay(BaseMerchant):
    api_id: int
    secret: str
    client: Optional[Payok] = None
    merchant: Literal[MerchantEnum.PAYOK]

    class Config:
        arbitrary_types_allowed = True

    @validator("client", always=True)
    def client_validator(cls, v, values):
        if not v:
            api_id = values.get("api_id")
            api_key = values.get("api_key").get_secret_value()
            secret = values.get("secret")
            shop_id = int(values.get("shop_id"))
            return Payok(api_id, api_key, secret, shop_id)

        return v

    @field_serializer('client')
    def serialize_cp(cp: Payok | None) -> typing.Any:
        return None

    async def create_invoice(
            self,
            user_id: int,
            amount: int | float | str,
            currency: str = "RUB",
            method: BTPaymentTypeRUB = BTPaymentTypeRUB.YooMoney,
            description: str = "Order",
            email: str = None,
            success_url: str = "https://example.com/success",
            fail_url: str = "https://example.com/fail",
            **kwargs
    ) -> Invoice:
        from ....db.models.invoice import Invoice

        payment_id = uuid.uuid4().hex
        payment_url = await self.client.create_pay(
            amount,
            payment_id,
            currency,
            desc=description
        )

        return Invoice(
            user_id=user_id,
            amount=float(amount),
            currency=currency,
            invoice_id=payment_id,
            pay_url=payment_url,
            description=description,
            merchant=self.merchant,
            expire_at=datetime.datetime.now() + datetime.timedelta(seconds=PAYMENT_LIFETIME)
        )

    async def is_paid(self, invoice_id: str) -> bool:
        try:
            transaction = await self.client.get_transactions(invoice_id)
            return transaction['transaction_status'] == PaymentStatus.PAID.value
        except Exception as e:
            return False
