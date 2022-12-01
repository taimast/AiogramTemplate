import abc
import zoneinfo
from abc import ABC
from functools import lru_cache
from pprint import pprint
from typing import Optional, Any

from aiohttp import ClientSession
from pydantic import BaseModel, SecretStr

# seconds
PAYMENT_LIFETIME = 60 * 60
TIME_ZONE = zoneinfo.ZoneInfo("Europe/Moscow")


# todo L1 15.10.2022 2:07 taima: add to config
# класс с методами для работы с мерчантами


class Merchant(BaseModel, ABC):
    shop_id: Optional[str]
    api_key: SecretStr
    create_url: Optional[str] = None
    status_url: Optional[str] = None
    session: Optional[ClientSession] = None

    class Config:
        arbitrary_types_allowed = True

    @property
    def headers(self) -> dict:
        return {}

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
    async def create_invoice(self, amount: int | float | str, **kwargs) -> Any:
        pass

    @abc.abstractmethod
    async def is_paid(self, invoice_id: str) -> bool:
        pass
