from __future__ import annotations

import datetime
import typing
from enum import Enum
from typing import Literal

from loguru import logger
from pydantic import BaseModel

from .base import BaseMerchant, MerchantEnum, PAYMENT_LIFETIME

if typing.TYPE_CHECKING:
    from ...db.models.invoice import Invoice


class Currency(str, Enum):
    RUB = "RUB"
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"


class CryptoCurrency(str, Enum):
    BTC = "BTC"
    ETH = "ETH"
    LTC = "LTC"
    USDT = "USDT"


class CryptoPaymentRequest(BaseModel):
    shop_id: str
    amount: float
    order_id: str | None = None
    currency: Currency = Currency.RUB
    email: str | None = None
    # expire_at - 24 часа


class Status(str, Enum):
    SUCCESS = "success"
    ERROR = "error"


class CryptoPaymentResponse(BaseModel):
    # todo L1 26.11.2022 0:45 taima: Переименовать invoice_id в id
    invoice_id: str
    status: Status
    pay_url: str
    currency: CryptoCurrency


class StatusInvoice(str, Enum):
    CREATED = "created"
    PAID = "paid"
    PARTIAL = "partial"
    CANCELED = "canceled"


class CryptoPayment(BaseModel):
    status: Status
    status_invoice: StatusInvoice
    error: str | None = None


class CryptoCloud(BaseMerchant):
    create_url: str = "https://api.cryptocloud.plus/v1/invoice/create"
    status_url: str = "https://api.cryptocloud.plus/v1/invoice/info"
    id_prefix: str = "INV-"
    merchant: Literal[MerchantEnum.CRYPTO_CLOUD]

    @property
    def headers(self) -> dict:
        return {"Authorization": f"Token {self.api_key.get_secret_value()}"}

    async def create_invoice(
            self,
            user_id: int,
            amount: int | float | str,
            currency: Currency = Currency.RUB,
            order_id: str = None,
            email: str = None,
    ) -> Invoice:
        from ...db.models.invoice import Invoice
        data = CryptoPaymentRequest(
            amount=amount,
            currency=Currency(currency),
            email=email,
            order_id=order_id,
            shop_id=self.shop_id,
        )
        response = await self.make_request("POST", self.create_url, json=data.dict())
        response = CryptoPaymentResponse(**response)
        if response.status == Status.SUCCESS:
            logger.info(f"Success create invoice {response.invoice_id}")
            return Invoice(
                user_id=user_id,
                amount=amount,
                currency=currency,
                invoice_id=response.invoice_id,
                pay_url=response.pay_url,
                order_id=order_id,
                email=email,
                merchant=self.merchant,
                expire_at=datetime.datetime.now() + datetime.timedelta(seconds=PAYMENT_LIFETIME)
            )
        logger.error(f"Error create invoice {response}")
        raise Exception(f"Error create invoice {response}")

    async def is_paid(self, invoice_id: str) -> bool:
        response = await self.make_request(
            "GET", self.status_url, params={"uuid": f"{self.id_prefix}{invoice_id}"}
        )
        response = CryptoPayment(**response)
        # logger.debug(f"Response from {self.status_url} is {response}")
        return response.status == Status.SUCCESS and response.status_invoice == StatusInvoice.PAID
