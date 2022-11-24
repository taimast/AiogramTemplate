from dataclasses import dataclass

import aiohttp
from loguru import logger

from .base import Merchant


@dataclass
class CryptoInvoiceRequest:
    amount: int | float | str
    shop_id: str = None
    order_id: str = None
    currency: str = "RUB"
    email: str = None

    # expire_at: datetime.datetime = field(
    #     default_factory=lambda: datetime.datetime.now(TIME_ZONE) + datetime.timedelta(seconds=PAYMENT_LIFETIME)
    # )

    def dict(self):
        return self.__dict__


class CryptoCloud(Merchant):
    create_url: str = "https://api.cryptocloud.plus/v1/invoice/create"
    status_url: str = "https://api.cryptocloud.plus/v1/invoice/info"
    id_prefix: str = "INV-"

    @property
    def headers(self) -> dict:
        return {"Authorization": f"Token {self.api_key.get_secret_value()}"}

    async def create_invoice(self,
                             amount: int | float | str,
                             currency: str = "RUB",
                             order_id: str = None,
                             email: str = None, ) -> dict | None:
        data = {
            "amount": amount,
            "currency": currency,
            "email": email,
            "order_id": order_id,
            # не принимает expire_at
            # "expire_at": datetime.datetime.now(TIME_ZONE) + datetime.timedelta(seconds=PAYMENT_LIFETIME),
            "shop_id": self.shop_id,
        }

        logger.debug(f"Sending request to {self.create_url} with data {data}")
        response = await self.make_request("POST", self.create_url, json=data)
        # todo L1 24.11.2022 17:12 taima: Сделать объектом получаемый ответ, error и success
        logger.debug(f"Response from {self.create_url} is {response}")
        return response

    async def is_paid(self, invoice_id: str) -> bool:
        response = await self.make_request(
            "GET", self.status_url, params={"uuid": f"{self.id_prefix}{invoice_id}"}
        )
        logger.debug(f"Response from {self.status_url} is {response}")
        # todo L1 24.11.2022 17:12 taima: Сделать объектом получаемый ответ, error и success
        return response["status_invoice"] == "paid"

