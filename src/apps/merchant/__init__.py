from typing import Annotated

from pydantic import Field

from .aaio.merchant import AaioPay
from .cryptocloud import CryptoCloud
from .cryptomus import Cryptomus
from .cryptopay import CryptoPay
from .payok.merchant import PayokPay
from .qiwi import Qiwi
from .yookassa import YooKassa
from .betatransfer import BetaTransferPay
MerchantAnnotated = Annotated[
    Qiwi | YooKassa | CryptoPay | CryptoCloud | Cryptomus | BetaTransferPay | PayokPay | AaioPay,
    Field(discriminator="merchant")
]
