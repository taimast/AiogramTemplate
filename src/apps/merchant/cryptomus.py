from __future__ import annotations

import asyncio
import typing
import uuid
from typing import Literal, Optional, Any

from pydantic import Field, validator

from .base import BaseMerchant, MerchantEnum

if typing.TYPE_CHECKING:
    from ...db.models.invoice import Invoice
    from ...db.models.invoice import Currency

try:
    from pyCryptomusAPI import Invoice as CryptomusInvoice, pyCryptomusAPI
except ImportError:
    pyCryptomusAPI = Any
    CryptomusInvoice = Any


class Cryptomus(BaseMerchant):
    merchant: Literal[MerchantEnum.CRYPTOMUS]
    create_url: str = "https://api.cryptomus.com/v1/payment"
    status_url: str = "https://api.cryptomus.com/v1/payment/info"
    client: Optional[pyCryptomusAPI] = Field(None, validate_default=True)

    @validator('client', always=True)
    def validate_client(cls, v, values):
        if v is None:
            merchant_uuid = values.get("shop_id")
            payment_api_key = values.get("api_key").get_secret_value()
            return pyCryptomusAPI(merchant_uuid, payment_api_key)
        return v

    async def create_invoice(
            self,
            user_id: int,
            amount: int | float | str,
            currency: 'Currency' = "USD",
            description: str | None = None,
            **kwargs
    ) -> Invoice:
        from ...db.models.invoice import Invoice
        order_id = uuid.uuid4().hex
        invoice: CryptomusInvoice = await asyncio.to_thread(
            self.client.create_invoice,
            amount=amount,
            order_id=order_id,
            currency=currency
        )
        return Invoice(
            user_id=user_id,
            amount=amount,
            currency=currency,
            invoice_id=invoice.order_id,
            pay_url=invoice.url,
            description=description,
            merchant=self.merchant,
        )

    async def is_paid(self, invoice_id: str) -> bool:
        invoice: CryptomusInvoice = self.client.payment_information(
            order_id=invoice_id
        )
        return invoice.is_final
