import abc
import zoneinfo
from abc import ABC
from typing import Optional, Any

from pydantic import BaseModel, SecretStr

# seconds
PAYMENT_LIFETIME = 60 * 60
TIME_ZONE = zoneinfo.ZoneInfo("Europe/Moscow")


# todo L1 15.10.2022 2:07 taima: add to config
# класс с методами для работы с мерчантами


class BaseMerchant(BaseModel, ABC):
    shop_id: Optional[str]
    api_key: SecretStr
    create_url: Optional[str] = None
    status_url: Optional[str] = None

    @abc.abstractmethod
    async def create_invoice(self, amount: int | float | str) -> Any:
        pass

    @abc.abstractmethod
    async def is_paid(self, invoice_id: str) -> bool:
        pass


class Merchant(BaseMerchant):

    async def create_invoice(self, amount: int | float | str) -> Any:
        pass

    async def is_paid(self, invoice_id: str) -> bool:
        pass
