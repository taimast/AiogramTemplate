import datetime
import uuid
from base64 import b64encode
from functools import lru_cache

import aiohttp
from pydantic import BaseModel

from .base import Merchant


class Confirmation(BaseModel):
    confirmation_url: str
    type: str


class Amount(BaseModel):
    currency: str
    value: float


class YooPayment(BaseModel):
    id: uuid.UUID
    amount: Amount
    description: str
    created_at: datetime.datetime
    confirmation: Confirmation | None
    paid: bool
    status: str

    def is_paid(self) -> bool:
        return self.paid


class Yookassa(Merchant):
    create_url: str = "https://api.yookassa.ru/v3/payments"

    @property
    @lru_cache
    def headers(self) -> dict:
        user_and_pass = b64encode(f"{self.shop_id}:{self.api_key}".encode()).decode("ascii")
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
        data = {
            "amount": {"value": amount, "currency": currency},
            "confirmation": {"type": "redirect", "return_url": return_url},
            "capture": True,
            "description": description or "Product {amount} {currency}",
            # "expires_at": str(datetime.datetime.now(tz) + datetime.timedelta(minutes=15))
        }
        async with aiohttp.ClientSession(headers=self.headers | {"Idempotence-Key": str(uuid.uuid4())}) as session:
            async with session.post(self.create_url, json=data) as response:
                return YooPayment.parse_obj(await response.json())

    async def is_paid(self, invoice_id: uuid.UUID) -> bool:
        return (await self.get_invoice(invoice_id)).is_paid()

    async def get_invoice(self, invoice_id: uuid.UUID) -> "YooPayment":
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(f"{self.create_url}/{invoice_id}") as response:
                res = await response.json()
                return YooPayment.parse_obj(res)

    async def cancel(self, bill_id: uuid.UUID) -> "YooPayment":
        async with aiohttp.ClientSession(headers=self.headers | {"Idempotence-Key": str(uuid.uuid4())}) as session:
            async with session.post(f"{self.create_url}/{bill_id}/cancel", json={}) as response:
                res = await response.json()
                return YooPayment.parse_obj(res)
