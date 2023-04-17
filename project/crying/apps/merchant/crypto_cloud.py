from enum import Enum

from loguru import logger
from pydantic import BaseModel

from .base import Merchant


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
                             email: str = None, ) -> CryptoPaymentResponse | None:
        data = CryptoPaymentRequest(
            amount=amount,
            currency=Currency(currency),
            email=email,
            order_id=order_id,
            shop_id=self.shop_id,
        )

        logger.debug(f"Sending request to {self.create_url} with data {data}")
        response = await self.make_request("POST", self.create_url, json=data.dict())
        response = CryptoPaymentResponse(**response)
        if response.status == Status.SUCCESS:
            logger.info(f"Success create invoice {response.invoice_id}")
            return response
        else:
            logger.error(f"Error create invoice {response}")
            return None

    async def is_paid(self, invoice_id: str) -> bool:
        response = await self.make_request(
            "GET", self.status_url, params={"uuid": f"{self.id_prefix}{invoice_id}"}
        )
        response = CryptoPayment(**response)
        # logger.debug(f"Response from {self.status_url} is {response}")
        return response.status == Status.SUCCESS and response.status_invoice == StatusInvoice.PAID
