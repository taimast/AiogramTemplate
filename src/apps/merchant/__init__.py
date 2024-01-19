from typing import Annotated

from pydantic import Field

from .cryptocloud import CryptoCloud
from .cryptomus import Cryptomus
from .cryptopay import CryptoPay
from .qiwi import Qiwi
from .yookassa import YooKassa

MerchantAnnotated = Annotated[
    Qiwi | YooKassa | CryptoPay | CryptoCloud | Cryptomus,
    Field(discriminator="merchant")
]
