from typing import Annotated

from pydantic import Field

from .base import BaseMerchant, MerchantEnum
from .cryptocloud import CryptoCloud
from .cryptopay import CryptoPay
from .qiwi import Qiwi
from .yookassa import YooKassa

MerchantAnnotated = Annotated[
    Qiwi | YooKassa | CryptoPay | CryptoCloud,
    Field(description="merchant")
]
