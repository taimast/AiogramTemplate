import requests
from pydantic import BaseModel
from pypayment import BetaTransferPayment, PaymentCreationError


class PaymentMethod(BaseModel):
    method: str
    currency: str
    commission: float
    minimum: int
    maximum: int


# Example data instantiation
methods = [
    PaymentMethod(method="P2R_TJS", currency="TJS", commission=9.5, minimum=100, maximum=10000),
    PaymentMethod(method="Card7", currency="UAH", commission=12.0, minimum=300, maximum=20000),
    PaymentMethod(method="Card10", currency="BYN", commission=10.0, minimum=30, maximum=10000),
    PaymentMethod(method="Card5", currency="UAH", commission=9.5, minimum=350, maximum=20000),
    PaymentMethod(method="P2R_KZT", currency="KZT", commission=11.0, minimum=5600, maximum=460000),
    PaymentMethod(method="Card6", currency="UZS", commission=12.0, minimum=50000, maximum=5500000),
    PaymentMethod(method="Card1", currency="AZN", commission=13.0, minimum=10, maximum=4000),
    PaymentMethod(method="Card4", currency="RUB", commission=8.5, minimum=100, maximum=60000),
    PaymentMethod(method="Card8", currency="RUB", commission=10.0, minimum=500, maximum=50000),
    PaymentMethod(method="P2R", currency="RUB", commission=8.5, minimum=100, maximum=50000),
    PaymentMethod(method="YooMoney", currency="RUB", commission=12.0, minimum=100, maximum=50000),
    PaymentMethod(method="Crypto", currency="USD", commission=2.0, minimum=5, maximum=5000)
]


class BetaTrans(BetaTransferPayment):

    def _create_url(self) -> str:
        if not self._payment_type or not self._locale:
            raise PaymentCreationError("You must specify payment_type and locale!")

        params = {
            "token": BetaTransferPayment._public_key
        }

        data = {
            "amount": self._amount_with_commission,
            "currency": self._payment_type.value.currency.value,
            "orderId": self.id,
            "paymentSystem": self._payment_type.value.name,
            "urlResult": self._url_result,
            "urlSuccess": self._url_success,
            "urlFail": self._url_fail,
            "locale": self._locale.value,
            "fullCallback": 1,
            "payerId": self.payer_id
        }
        # delete NOne
        data = {key: value for key, value in data.items() if value}
        data["sign"] = self._get_sign(data)
        try:
            response = requests.post(
                BetaTransferPayment._PAYMENT_URL,
                headers=self._get_headers(),
                params=params,
                data=data
            )
        except Exception as e:
            raise PaymentCreationError(e)

        if response.status_code != 200:
            raise PaymentCreationError(response.text)

        return str(response.json().get("url"))
