from dataclasses import dataclass
from enum import Enum
from typing import Optional


class BTCurrency(Enum):
    """BetaTransfer payment currency enum."""
    RUB = "RUB"
    UAH = "UAH"
    USD = "USD"
    KZT = "KZT"
    UZS = "UZS"
    BYN = "BYN"
    AZN = "AZN"
    TJS = "TJS"


@dataclass
class BTGateway:
    name: str
    currency: BTCurrency
    commission_in_percent: float
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    description: Optional[str] = None


class BTPaymentType(Enum):
    """BetaTransfer payment type enum."""
    YooMoney = BTGateway("YooMoney", BTCurrency.RUB, 12.0, 100, 50000, "YooMoney RUB")
    P2R = BTGateway("P2R", BTCurrency.RUB, 8.5, 100, 50000, "Visa/Mastercard/МИР P2P RUB")
    Card4 = BTGateway("Card4", BTCurrency.RUB, 8.5, 100, 60000, "Cascade SBP RUB")
    Card8 = BTGateway("Card8", BTCurrency.RUB, 10.0, 500, 50000, "SberPay RUB")

    Card5 = BTGateway("Card5", BTCurrency.UAH, 9.5, 350, 20000, "Visa/Mastercard Украина П2П UAH")
    Card7 = BTGateway("Card7", BTCurrency.UAH, 12.0, 300, 20000, "Visa/Mastercard Украина QR UAH")

    Card6 = BTGateway("Card6", BTCurrency.UZS, 12.0, 50000, 5500000, "Visa/Mastercard UZS")

    P2R_KZT = BTGateway("P2R_KZT", BTCurrency.KZT, 11.0, 5600, 460000, "Visa/Mastercard P2R KZT")

    Card10 = BTGateway("Card10", BTCurrency.BYN, 10.0, 30, 10000, "Visa/Mastercard Belarus BYN")

    P2R_TJS = BTGateway("P2R_TJS", BTCurrency.TJS, 9.5, 100, 10000, "P2R TJS")
    Card1 = BTGateway("Card1", BTCurrency.AZN, 13.0, 10, 4000, "AZN")
    Crypto = BTGateway("Crypto", BTCurrency.USD, 2.0, 5, 5000, "Crypto USD")


class BTPaymentTypeRUB(Enum):
    """BetaTransfer payment type enum."""
    YooMoney = BTGateway("YooMoney", BTCurrency.RUB, 12.0, 100, 50000, "YooMoney RUB")
    P2R = BTGateway("P2R", BTCurrency.RUB, 8.5, 100, 50000, "Visa/Mastercard/МИР P2P RUB")
    Card4 = BTGateway("Card4", BTCurrency.RUB, 8.5, 100, 60000, "Cascade SBP RUB")
    Card8 = BTGateway("Card8", BTCurrency.RUB, 10.0, 500, 50000, "SberPay RUB")

    Card5 = BTGateway("Card5", BTCurrency.RUB, 9.5, 800, 50000, "Visa/Mastercard Украина П2П UAH")
    Card7 = BTGateway("Card7", BTCurrency.RUB, 12.0, 800, 50000, "Visa/Mastercard Украина QR UAH")

    Card6 = BTGateway("Card6", BTCurrency.RUB, 12.0, 400, 40000, "Visa/Mastercard UZS")

    P2R_KZT = BTGateway("P2R_KZT", BTCurrency.RUB, 11.0, 1300, 94000, "Visa/Mastercard P2R KZT")

    Card10 = BTGateway("Card10", BTCurrency.RUB, 10.0, 900, 270000, "Visa/Mastercard Belarus BYN")

    P2R_TJS = BTGateway("P2R_TJS", BTCurrency.RUB, 9.5, 900, 80000, "P2R TJS")
    Card1 = BTGateway("Card1", BTCurrency.RUB, 13.0, 600, 200000, "AZN")
    Crypto = BTGateway("Crypto", BTCurrency.RUB, 2.0, 500, 450000, "Crypto USD")
