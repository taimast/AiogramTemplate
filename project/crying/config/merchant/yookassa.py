import datetime
import uuid
from base64 import b64encode
from enum import Enum
from pprint import pprint
from typing import Optional

from pydantic import BaseModel, validator

from .base import Merchant


class Amount(BaseModel):
    currency: str
    value: float


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


class YooPaymentRequest(BaseModel):
    amount: Amount
    description: str | None
    confirmation: ConfirmationRequest
    capture: bool = True

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
    confirmation: Confirmation
    paid: bool
    status: Status
    recipient: Recipient | None
    income_amount: Amount | None

    def is_paid(self) -> bool:
        return self.paid


class YooKassa(Merchant):
    create_url: str = "https://api.yookassa.ru/v3/payments"

    @property
    def headers(self) -> dict:
        user_and_pass = b64encode(f"{self.shop_id}:{self.api_key.get_secret_value()}".encode()).decode("ascii")
        return {
            "Authorization": f"Basic {user_and_pass}",
            "Content-type": "application/json",
        }

    async def create_invoice(
            self,
            amount: int | float | str,
            description: str = None,
            currency: str = "RUB",
            return_url: str = f"https://t.me/"  # todo L2 14.08.2022 19:02 taima: прописать url
    ) -> "YooPayment":
        """ Создание платежа """

        data = YooPaymentRequest(
            amount=Amount(currency=currency, value=amount),
            confirmation=Confirmation(return_url=return_url),
            description=description,
        )
        idempotence_key = {"Idempotence-Key": str(uuid.uuid4())}
        response = await self.make_request("POST", self.create_url, json=data.dict(), headers=idempotence_key)
        return YooPayment(**response)

    async def is_paid(self, invoice_id: uuid.UUID) -> bool:
        """ Проверка статуса платежа """
        return (await self.get_invoice(invoice_id)).paid

    async def get_invoice(self, invoice_id: uuid.UUID) -> "YooPayment":
        """ Получение информации о платеже """
        res = await self.make_request("GET", f"{self.create_url}/{invoice_id}")
        return YooPayment.parse_obj(res)

    async def cancel(self, bill_id: uuid.UUID) -> "YooPayment":
        """ Отмена платежа """
        idempotence_key = {"Idempotence-Key": str(uuid.uuid4())}
        res = await self.make_request("POST", f"{self.create_url}/{bill_id}/cancel", headers=idempotence_key)
        return YooPayment.parse_obj(res)
