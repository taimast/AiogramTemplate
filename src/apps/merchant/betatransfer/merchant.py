from __future__ import annotations

import datetime
import typing
from typing import Optional, Literal

from pydantic import validator, field_serializer
from pypayment import PaymentStatus

from src.apps.merchant.base import BaseMerchant, MerchantEnum, PAYMENT_LIFETIME
from src.apps.merchant.betatransfer.betatransfer import BetaTrans
from src.apps.merchant.betatransfer.methods import BTPaymentTypeRUB

if typing.TYPE_CHECKING:
    from src.db.models.invoice import Invoice


class BetaTransferPay(BaseMerchant):
    public_key: str
    client: Optional[BetaTrans] = None
    merchant: Literal[MerchantEnum.BETA_TRANSFER_PAY]

    class Config:
        arbitrary_types_allowed = True

    @validator("client", always=True)
    def client_validator(cls, v, values):
        if not v:
            api_key = values.get("api_key")
            v = BetaTrans.authorize(values["public_key"], api_key.get_secret_value())
        return v

    @field_serializer('client')
    def serialize_cp(cp: BetaTrans | None) -> typing.Any:
        return None

    async def create_invoice(
            self,
            user_id: int,
            amount: int | float | str,
            currency: str = "RUB",
            method: BTPaymentTypeRUB = BTPaymentTypeRUB.YooMoney,
            description: str = "Test Order",
            email: str = None,
            success_url: str = "https://example.com/success",
            fail_url: str = "https://example.com/fail",
            **kwargs
    ) -> Invoice:
        from ....db.models.invoice import Invoice
        payment = BetaTrans(
            amount,
            url_success=success_url,
            url_fail=fail_url,
            payment_type=method,
        )

        return Invoice(
            user_id=user_id,
            amount=float(amount),
            currency=currency,
            invoice_id=payment.id,
            pay_url=payment.url,
            description=description,
            merchant=self.merchant,
            expire_at=datetime.datetime.now() + datetime.timedelta(seconds=PAYMENT_LIFETIME)
        )

    async def is_paid(self, invoice_id: str) -> bool:
        status, income = BetaTrans.get_status_and_income(invoice_id)
        return status == PaymentStatus.PAID
