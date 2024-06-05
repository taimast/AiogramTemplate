from __future__ import annotations

import abc
import zoneinfo
from abc import ABC
from enum import StrEnum
from typing import Optional, Any, Literal, TYPE_CHECKING

from aiohttp import ClientSession
from pydantic import BaseModel, SecretStr, field_serializer

if TYPE_CHECKING:
    from ...db.models.invoice import Invoice

# seconds
PAYMENT_LIFETIME = 60 * 60
TIME_ZONE = zoneinfo.ZoneInfo("Europe/Moscow")


# todo L1 15.10.2022 2:07 taima: add to config
# класс с методами для работы с мерчантами

class MerchantEnum(StrEnum):
    NONE = "none"
    CRYPTO_CLOUD = "crypto_cloud"
    USDT = "usdt"
    QIWI = "qiwi"
    YOOMONEY = "yoomoney"
    YOOKASSA = "yookassa"
    CRYPTO_PAY = "crypto_pay"
    CRYPTOMUS = "cryptomus"
    WALLET_PAY = "wallet_pay"
    STRIPE = "stripe"
    TRIBUTE = "tribute"
    BETA_TRANSFER_PAY = "beta_transfer_pay"
    PAYOK = "payok"
    AAIO = "aaio"


class BaseMerchant(BaseModel, ABC):
    shop_id: Optional[str] = None
    api_key: SecretStr
    create_url: Optional[str] = None
    status_url: Optional[str] = None
    session: Optional[ClientSession] = None
    merchant: Literal[MerchantEnum.NONE]

    class Config:
        arbitrary_types_allowed = True

    @property
    def headers(self) -> dict:
        return {}

    @field_serializer("session")
    def serialize_session(self, v: ClientSession) -> None:
        pass

    @field_serializer("api_key")
    def serialize_api_key(self, v: SecretStr) -> str:
        return v.get_secret_value()

    async def get_session(self):
        if self.session is None or self.session.closed:
            self.session = ClientSession(headers=self.headers)
        return self.session

    async def close_session(self):
        if self.session is not None:
            await self.session.close()

    async def make_request(self, method: str, url: str, **kwargs) -> Any:
        session = await self.get_session()
        async with session.request(method, url, **kwargs) as res:
            return await res.json()

    @abc.abstractmethod
    async def create_invoice(
            self,
            user_id: int,
            amount: int | float | str,
            **kwargs
    ) -> Invoice:
        pass

    @abc.abstractmethod
    async def is_paid(self, invoice_id: str) -> bool:
        pass
