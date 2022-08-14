import abc
import datetime
import uuid
from abc import ABC
from base64 import b64encode
from functools import lru_cache
from typing import Optional, Any

import aiohttp
from glQiwiApi import QiwiP2PClient
from glQiwiApi.qiwi.clients.p2p.types import Bill
from pydantic import BaseModel, SecretStr, validator

from project.crying.config import config, TIME_ZONE
from project.crying.config.config import PAYMENT_LIFETIME
from project.crying.config.yookassa_models import YooPayment


class Merchant(BaseModel, ABC):
    shop_id: Optional[str]
    api_key: SecretStr
    create_url: Optional[str]
    status_url: Optional[str]

    @abc.abstractmethod
    async def create_invoice(self, amount: int | float | str) -> Any:
        pass

    @abc.abstractmethod
    async def is_paid(self, invoice_id: str) -> bool:
        pass


class CryptoCloud(Merchant):
    create_url: str = "https://cryptocloud.pro/api/v2/invoice/create"
    status_url: str = "https://cryptocloud.plus/api/v2/invoice/status"

    @property
    @lru_cache
    def headers(self) -> dict:
        return {"Authorization": f"Token {self.api_key}"}

    async def create_invoice(self,
                             amount: int | float | str,
                             currency: str = "RUB",
                             order_id: str = None,
                             email: str = None, ):
        data = {
            "amount": amount,
            "currency": currency,
            "email": email,
            "order_id": order_id,
            "expire_at": datetime.datetime.now(TIME_ZONE) + datetime.timedelta(minutes=PAYMENT_LIFETIME),
            "shop_id": self.shop_id,
        }
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.post(self.create_url, data=data) as res:
                result_data = await res.json()
                return result_data

    async def is_paid(self, invoice_id: str) -> bool:
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(self.status_url, params={"uuid": invoice_id}) as res:
                result = await res.json()
                return result["status_invoice"] == "paid"


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


class Qiwi(Merchant):
    client: Optional[QiwiP2PClient]

    class Config:
        arbitrary_types_allowed = True

    @validator("client", always=True)
    def client_validator(cls, v, values):
        if not v:
            v = QiwiP2PClient(secret_p2p=values.get("api_key"))
        return v

    async def create_invoice(
            self,
            amount: int | float | str,
            description: str = None,
            order_id: str = None,
            email: str = None,
    ) -> Bill:
        async with self.client:
            return await self.client.create_p2p_bill(
                amount=amount,
                comment=description or f"Product {amount}",
                expire_at=datetime.datetime.now(TIME_ZONE) + datetime.timedelta(minutes=PAYMENT_LIFETIME),
            )

    async def is_paid(self, invoice_id: str) -> bool:
        async with self.client:
            return (await config.payment.qiwi.get_bill_status(invoice_id)) == "PAID"
