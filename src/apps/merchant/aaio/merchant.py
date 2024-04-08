from __future__ import annotations

import datetime
import typing
import uuid
from typing import Optional, Literal

from AaioAPI import AaioAPI
from pydantic import validator, field_serializer

from src.apps.merchant.base import BaseMerchant, MerchantEnum, PAYMENT_LIFETIME
from src.apps.merchant.betatransfer.betatransfer import BetaTrans

if typing.TYPE_CHECKING:
    from src.db.models.invoice import Invoice


class AaioPay(BaseMerchant):
    secret_key1: str
    secret_key2: str
    client: Optional[AaioAPI] = None
    merchant: Literal[MerchantEnum.AAIO]

    class Config:
        arbitrary_types_allowed = True

    @validator("client", always=True)
    def client_validator(cls, v, values):
        if not v:
            api_key = values.get("api_key").get_secret_value()
            shop_id = values.get("shop_id")
            secret_key1 = values.get("secret_key1")
            v = AaioAPI(api_key, secret_key1, shop_id)
        return v

    @field_serializer('client')
    def serialize_cp(cp: BetaTrans | None) -> typing.Any:
        return None

    async def create_invoice(
            self,
            user_id: int,
            amount: int | float | str,
            currency: str = "RUB",
            description: str = "Order",
            email: str = None,
            success_url: str = "https://example.com/success",
            fail_url: str = "https://example.com/fail",
            **kwargs
    ) -> Invoice:
        from ....db.models.invoice import Invoice
        payment_id = uuid.uuid4().hex
        payment_url = self.client.create_payment(
            payment_id,
            amount=amount,
            currency=currency,
            description=description,
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
        info = self.client.get_payment_info(invoice_id)
        return info['status'] == "success"
