from __future__ import annotations

import datetime
import typing
from typing import Literal

from pydantic import validator
from stripe import StripeClient, checkout

from base import BaseMerchant, MerchantEnum, PAYMENT_LIFETIME

if typing.TYPE_CHECKING:
    from ...db.models.invoice import Invoice, Currency


class StripeMerchant(BaseMerchant):
    cp: StripeClient | None = None
    merchant: Literal[MerchantEnum.STRIPE]

    @validator('cp', always=True)
    def validate_cp(cls, v, values):
        return v or StripeClient(values.get("api_key").get_secret_value())

    async def create_invoice_object(
            self,
            amount: int | float | str,
            currency: Currency = "USD",
            description: str | None = None,
    ) -> checkout.Session:
        # [{
        #                 'price_data': {
        #                     'currency': currency,
        #                     'product_data': {
        #                         'name': 'ChatGPT Premium',
        #                     },
        #                     'unit_amount': amount,
        #                 },
        #                 'quantity': 1,
        #             }]
        line_item = checkout.SessionService.CreateParamsLineItem(
            price_data=checkout.SessionService.CreateParamsLineItemPriceData(
                currency=currency,
                product_data=checkout.SessionService.CreateParamsLineItemPriceDataProductData(
                    name=description or "ChatGPT Premium"
                ),
                unit_amount=amount
            ),
            quantity=1
        )

        params = checkout.SessionService.CreateParams(
            payment_method_types=["card"],
            line_items=[line_item],
            mode="payment",
            success_url='https://yourwebsite.com/success',
            cancel_url='https://yourwebsite.com/cancel',
        )

        invoice = self.cp.checkout.sessions.create(
            params=params
        )
        return invoice

    async def create_invoice(
            self,
            user_id: int,
            amount: int | float | str,
            currency: Currency = "USD",
            description: str | None = None,
            **kwargs
    ) -> Invoice:
        from ...db.models.invoice import Invoice
        invoice = await self.create_invoice_object(amount, currency, description)
        expired_at = datetime.datetime.now() + datetime.timedelta(seconds=PAYMENT_LIFETIME)
        return Invoice(
            user_id=user_id,
            amount=amount,
            currency=currency,
            invoice_id=invoice.id,
            pay_url=invoice.url,
            description=description,
            merchant=self.merchant,
            expire_at=expired_at
        )

    async def is_paid(self, invoice_id: str) -> bool:
        invoice = await self.cp.checkout.sessions.retrieve(invoice_id)
        return invoice.payment_status == "paid"


import asyncio


async def main():
    api_key = "api_key"
    stripe = StripeMerchant(api_key=api_key, merchant=MerchantEnum.STRIPE)
    invoice = await stripe.create_invoice_object(100, "usd", "test")
    print(invoice.url)
    while True:
        invoice = stripe.cp.checkout.sessions.retrieve(invoice.id)
        print(invoice.payment_status)
        if invoice.payment_status == "paid":
            break
        await asyncio.sleep(1)


if __name__ == '__main__':
    asyncio.run(main())
