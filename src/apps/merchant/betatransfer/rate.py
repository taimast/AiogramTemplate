import asyncio
import json

import aiohttp
from pydantic import BaseModel

url = "https://www.cbr-xml-daily.ru/latest.js"


# {'base': 'RUB',
#  'date': '2024-04-04',
#  'disclaimer': 'https://www.cbr-xml-daily.ru/#terms',
#  'rates': {'AED': 0.03975,
#            'AMD': 4.21823458,
#            'AUD': 0.016603435,
#            'AZN': 0.0184004,
#            'BGN': 0.01969438,
#            'BRL': 0.05463,
#            'BYN': 0.0352822,
#            'CAD': 0.01469002577,
#            'CHF': 0.00983123699,
#            'CNY': 0.07865,
#            'CZK': 0.25451056,
#            'DKK': 0.075101,
#            'EGP': 0.513023,
#            'EUR': 0.010057559,
#            'GBP': 0.008612856,
#            'GEL': 0.029022858,
#            'HKD': 0.084588,
#            'HUF': 3.9533817,
#            'IDR': 172.46612765,
#            'INR': 0.902926,
#            'JPY': 1.640019,
#            'KGS': 0.9671086,
#            'KRW': 14.600181,
#            'KZT': 4.8439755,
#            'MDL': 0.1914194,
#            'NOK': 0.11789477655,
#            'NZD': 0.01816223599,
#            'PLN': 0.04312519676,
#            'QAR': 0.0393986,
#            'RON': 0.0499398,
#            'RSD': 1.176275,
#            'SEK': 0.1163789,
#            'SGD': 0.0146229,
#            'THB': 0.396896,
#            'TJS': 0.1185885,
#            'TMT': 0.0378832,
#            'TRY': 0.34808397,
#            'UAH': 0.4256297,
#            'USD': 0.0108237759,
#            'UZS': 136.7424128,
#            'VND': 259.9874166,
#            'XDR': 0.00819151768,
#            'ZAR': 0.20406289},
#  'timestamp': 1712178000}


class RateInfo(BaseModel):
    base: str = "RUB"
    date: str
    rates: dict[str, float]
    timestamp: int

    # Получить эквивалент указанной валюты для рубля
    def get_equivalent(self, currency: str, roubles: float) -> float:
        rate = self.rates.get(currency)
        if rate is None:
            raise ValueError(f"Currency {currency} not found")
        return roubles * rate

    @classmethod
    async def fetch(cls):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as res:
                text = await res.text()
                data = json.loads(text)
                return cls(**data)


async def main():
    rate_info = await RateInfo.fetch()
    # eq = rate_info.get_equivalent("KZT", 100)
    eq = rate_info.get_equivalent("UAH", 250)
    print(eq)


if __name__ == '__main__':
    asyncio.run(main())
