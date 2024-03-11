from __future__ import annotations

import datetime
import typing
import uuid
from typing import Optional, Literal

from WalletPay import AsyncWalletPayAPI
from pydantic import validator

from .base import BaseMerchant, MerchantEnum, PAYMENT_LIFETIME

if typing.TYPE_CHECKING:
    from ...db.models.invoice import Invoice


class WalletPay(BaseMerchant):
    client: Optional[AsyncWalletPayAPI]
    merchant: Literal[MerchantEnum.WALLET_PAY]

    class Config:
        arbitrary_types_allowed = True

    @validator("client", always=True)
    def client_validator(cls, v, values):
        if not v:
            api_key = values.get("api_key")
            v = AsyncWalletPayAPI(api_key=api_key.get_secret_value())
        return v

    async def create_invoice(
            self,
            user_id: int,
            amount: int | float | str,
            currency: str = "USD",
            description: str = "Test Order",
            email: str = None,
            **kwargs
    ) -> Invoice:
        from ...db.models.invoice import Invoice
        external_id = str(uuid.uuid4())
        order = await self.client.create_order(
            amount=amount,
            currency_code=currency,
            description=description,
            external_id=external_id,
            timeout_seconds=PAYMENT_LIFETIME,
            customer_telegram_user_id=str(user_id),
        )

        return Invoice(
            user_id=user_id,
            amount=float(amount),
            currency=currency,
            invoice_id=order.id,
            pay_url=order.pay_link,
            description=description,
            merchant=self.merchant,
            expire_at=datetime.datetime.now() + datetime.timedelta(seconds=PAYMENT_LIFETIME)
        )

    async def is_paid(self, invoice_id: str) -> bool:
        order_preview = self.api.get_order_preview(order_id=invoice_id)
        return order_preview.status == "PAID"
