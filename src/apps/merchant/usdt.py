from __future__ import annotations

import typing
from enum import StrEnum
from typing import ClassVar

from loguru import logger
from pydantic import SecretStr, BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseMerchant

if typing.TYPE_CHECKING:
    from ...db.models.invoice import Invoice, Currency
    from ...db.models import User


class State(StrEnum):
    SUCCESS = "success"
    FAIL = "fail"
    PENDING = "pending"


class TransactionList(BaseModel):
    amount: float
    blockHash: str
    challengeStatus: str
    from_: str = Field(..., alias="from")
    height: str
    isFromContract: bool
    isToContract: bool
    l1OriginHash: str
    methodId: str
    state: State
    to: str
    tokenContractAddress: str
    tokenId: str
    transactionSymbol: str
    transactionTime: str
    txFee: str
    txId: str


class Data(BaseModel):
    chainFullName: str
    chainShortName: str
    limit: str
    page: str
    totalPage: str
    transactionLists: list[TransactionList]


class TransactionResponse(BaseModel):
    code: str
    data: list[Data]

    def is_success(self) -> bool:
        return self.code == "0"

    def is_paid(self, amount: float, to: str) -> bool:
        for data in self.data:
            for transaction in data.transactionLists:
                if transaction.amount == amount:
                    if transaction.to == to:
                        if transaction.state == State.SUCCESS:
                            return True
        return False


class USDT(BaseMerchant):
    address: str
    api_key: SecretStr
    base_url: ClassVar[str] = "https://www.oklink.com/"
    status_url: str = "https://www.oklink.com/api/v5/explorer/address/transaction-list"

    async def create_invoice(
            self,
            session: AsyncSession,
            user: User,
            amount: int | float | str,
            currency: Currency = "USDT",
            **kwargs
    ) -> Invoice:
        pass

    @property
    def headers(self) -> dict:
        return {
            "Ok-Access-Key": self.api_key.get_secret_value(),
        }

    async def get_transaction_response(self) -> TransactionResponse:
        """
        Get transaction response from USDT
        Throttling: 5 requests per second
        :return:
        """
        logger.info("Get transaction response from USDT")
        params = {
            "chainShortName": "TRON",
            "address": self.address,
            "protocolType": "token_20",
            "limit": 50,
        }
        response = await self.make_request("GET", self.status_url, params=params)
        return TransactionResponse(**response)

    async def is_paid(self, invoice_id: str) -> bool:
        response = await self.get_transaction_response()
        return response.is_paid(float(invoice_id), to=self.address)
