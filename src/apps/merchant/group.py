from pydantic import BaseModel, root_validator

from .base import BaseMerchant


# todo L1 23.11.2022 5:27 taima: Подумать что делать с этим
class MerchantGroup(BaseModel):
    merchants: dict[str, BaseMerchant]

    class Config:
        allow_mutation = False

    def get_merchant(self, name: str) -> BaseMerchant:
        return self.merchants[name]

    @root_validator(pre=True)
    def validate_merchants(cls, values):

        try:
            parsed_merchants = {}
            for merchant_name, merchant in values["merchants"].items():

                match merchant_name:
                    case "qiwi":
                        from .qiwi import Qiwi
                        parsed_merchants[merchant_name] = Qiwi(**merchant)
                    case "yookassa":
                        from .yookassa import YooKassa
                        parsed_merchants[merchant_name] = YooKassa(**merchant)
                    case "crypto_cloud":
                        from .crypto_cloud import CryptoCloud
                        parsed_merchants[merchant_name] = CryptoCloud(**merchant)
                    case _:
                        raise ValueError(f"Merchant {merchant_name} not found")
        except ImportError as e:
            raise ImportError(f"Don't forget to install extra requirements for merchant: {e.name}")
        values["merchants"] = parsed_merchants
        return values
