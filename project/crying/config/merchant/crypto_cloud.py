import datetime

import aiohttp
from loguru import logger

from .base import Merchant, TIME_ZONE, PAYMENT_LIFETIME


class CryptoCloud(Merchant):
    create_url: str = "https://api.cryptocloud.plus/v1/invoice/create"
    status_url: str = "https://api.cryptocloud.plus/v1/invoice/info"
    id_prefix = "INV-"
    @property
    def headers(self) -> dict:
        return {"Authorization": f"Token {self.api_key.get_secret_value()}"}

    async def create_invoice(self,
                             amount: int | float | str,
                             currency: str = "RUB",
                             order_id: str = None,
                             email: str = None, ) -> dict|None:
        data = {
            "amount": amount,
            "currency": currency,
            "email": email,
            "order_id": order_id,
            "expire_at": datetime.datetime.now(TIME_ZONE) + datetime.timedelta(seconds=PAYMENT_LIFETIME),
            "shop_id": self.shop_id,
        }
        logger.debug(f"Sending request to {self.create_url} with data {data}")
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.post(self.create_url, data=data) as res:
                result_data = await res.json()

                if result_data["status"] == "success":
                    logger.success(f"Success create invoice {result_data['invoice_id']}")
                    return result_data
                else:
                    logger.error(f"Error create invoice {result_data}")
                    return None

    async def is_paid(self, invoice_id: str) -> bool:
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(self.status_url, params={"uuid": f"{self.id_prefix}{invoice_id}"}) as res:
                result = await res.json()
                if result["status"] == "success":
                    return result["status_invoice"] == "paid"
                else:
                    logger.error(f"Error check payment {invoice_id} {result}")
                    return False

