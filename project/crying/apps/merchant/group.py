from typing import Optional

from pydantic import BaseModel, root_validator

from .base import Merchant


# todo L1 23.11.2022 5:27 taima: Подумать что делать с этим
class MerchantGroup(BaseModel):
    qiwi: Optional[Merchant]
    yookassa: Optional[Merchant]
    crypto_cloud: Optional[Merchant]

    class Config:
        allow_mutation = False

    def get_merchant(self, name: str) -> Merchant:
        merchant = getattr(self, name)
        if merchant is None:
            raise ValueError(f"Merchant {name} not found")
        return merchant

    @root_validator(pre=True)
    def validate_merchants(cls, values):
        try:
            if qiwi := values.get("qiwi"):
                from .qiwi import Qiwi
                values["qiwi"] = Qiwi(**qiwi)
            if yookassa := values.get("yookassa"):
                from .yookassa import YooKassa
                values["yookassa"] = YooKassa(**yookassa)
            if crypto_cloud := values.get("crypto_cloud"):
                from .crypto_cloud import CryptoCloud
                values["crypto_cloud"] = CryptoCloud(**crypto_cloud)
        except ImportError as e:
            raise ImportError(f"Don't forget to install extra requirements for merchant: {e.name}")
        return values
