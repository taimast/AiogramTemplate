from __future__ import annotations

import datetime
import typing
import uuid
from base64 import b64encode
from enum import Enum
from typing import Optional, Literal

from pydantic import BaseModel, validator

from .base import BaseMerchant, MerchantEnum, PAYMENT_LIFETIME

if typing.TYPE_CHECKING:
    from ...db.models.invoice import Invoice


class Amount(BaseModel):
    currency: str
    value: str


class Confirmation(BaseModel):
    confirmation_url: Optional[str]
    type: str = "redirect"


class ConfirmationRequest(BaseModel):
    return_url: Optional[str]
    type: str = "redirect"


class Recipient(BaseModel):
    account_id: str
    gateway_id: str


class Status(str, Enum):
    WAITING_FOR_CAPTURE = "waiting_for_capture"
    SUCCEEDED = "succeeded"
    CANCELED = "canceled"
    PENDING = "pending"


class Customer(BaseModel):
    email: str


class Item(BaseModel):
    description: str = "Товар"
    quantity: int = 1
    amount: Amount = Amount(currency="RUB", value='250.0')
    vat_code: int = 1
    payment_subject: str = "commodity"
    payment_mode: str = "full_payment"


class Receipt(BaseModel):
    customer: Customer = Customer(email="some@gmail.com")
    items: list[Item] = [Item()]


class YooPaymentRequest(BaseModel):
    amount: Amount
    description: str | None
    confirmation: ConfirmationRequest | None
    capture: bool = True
    receipt: Receipt | None = None

    # необязательный expire_at. Не указано в документации. Всегда равен 1 часу
    # "expires_at": str(datetime.datetime.now(TIME_ZONE) + datetime.timedelta(minutes=15))

    @validator("description", always=True)
    def description_validator(cls, v, values):
        if not v:
            v = f"Product {values.get('amount')}"
        return v


class YooPayment(YooPaymentRequest):
    id: uuid.UUID
    created_at: datetime.datetime
    confirmation: Confirmation | None = None
    paid: bool
    status: Status
    recipient: Recipient | None = None
    income_amount: Amount | None = None

    def is_paid(self) -> bool:
        return self.paid


class YooKassa(BaseMerchant):
    create_url: str = "https://api.yookassa.ru/v3/payments"
    merchant: Literal[MerchantEnum.YOOKASSA]

    @property
    def headers(self) -> dict:
        user_and_pass = b64encode(f"{self.shop_id}:{self.api_key.get_secret_value()}".encode()).decode("ascii")
        return {
            "Authorization": f"Basic {user_and_pass}",
            "Content-type": "application/json",
        }

    async def create_invoice(
            self,
            user_id: int,
            amount: int | float | str,
            description: str = None,
            currency: str = "RUB",
            return_url: str = "https://t.me/"  # todo L2 14.08.2022 19:02 taima: прописать url
    ) -> Invoice:
        from ...db.models.invoice import Invoice
        data = YooPaymentRequest(
            amount=Amount(currency=currency, value=str(amount)),
            confirmation=ConfirmationRequest(return_url=return_url),
            description=description,
            receipt=Receipt(items=[Item(amount=Amount(currency=currency, value=str(float(amount))))])
        )
        idempotence_key = {"Idempotence-Key": str(uuid.uuid4())}
        response = await self.make_request(
            "POST",
            self.create_url,
            json=data.model_dump(),
            headers=idempotence_key
        )
        if response.get("type") == "error":
            raise Exception(response)
        yoo_payment = YooPayment(**response)
        return Invoice(
            user_id=user_id,
            amount=float(yoo_payment.amount.value),
            currency=yoo_payment.amount.currency,
            invoice_id=str(yoo_payment.id),
            pay_url=yoo_payment.confirmation.confirmation_url,
            description=description,
            merchant=self.merchant,
            expire_at=datetime.datetime.now() + datetime.timedelta(seconds=PAYMENT_LIFETIME)
        )

    async def is_paid(self, invoice_id: uuid.UUID) -> bool:
        """ Проверка статуса платежа """
        return (await self.get_invoice(invoice_id)).paid

    async def get_invoice(self, invoice_id: uuid.UUID) -> YooPayment:
        """ Получение информации о платеже """
        res = await self.make_request("GET", f"{self.create_url}/{invoice_id}")
        return YooPayment.parse_obj(res)

    async def cancel(self, bill_id: uuid.UUID) -> YooPayment:
        """ Отмена платежа """
        idempotence_key = {"Idempotence-Key": str(uuid.uuid4())}
        res = await self.make_request("POST", f"{self.create_url}/{bill_id}/cancel", headers=idempotence_key)
        return YooPayment.parse_obj(res)
