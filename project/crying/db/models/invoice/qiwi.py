from typing import Self

from glQiwiApi.qiwi.clients.p2p.types import Bill
from loguru import logger
from tortoise import fields

from project.crying.config.merchant.base import Merchant
from .base import AbstractInvoice
from ..subscription.subscription import SubscriptionTemplate
from ..user import User


class InvoiceQiwi(AbstractInvoice):
    """{'amount': {'currency': 'RUB', 'value': 5.0},
         'created_at': datetime.datetime(2022, 5, 22, 21, 24, 17, 186000, tzinfo=datetime.timezone(datetime.timedelta(seconds=10800))),
         'custom_fields': {'pay_sources_filter': 'qw', 'theme_code': 'Yvan-YKaSh'},
         'customer': None,
         'expire_at': datetime.datetime(2022, 5, 22, 21, 54, 7, tzinfo=datetime.timezone(datetime.timedelta(seconds=10800))),
         'id': '397a2a00-19ae-40f6-9ea1-c4e3bccb315f',
         'pay_url': 'https://oplata.qiwi.com/form/?invoice_uid=f8b7366e-3b5d-44e0-9356-50c56eab18d6',
         'recipientPhoneNumber': '79898600122',
         'site_id': '7l0erf-00',
         'status': {'changed_datetime': datetime.datetime(2022, 5, 22, 21, 24, 17, 186000, tzinfo=datetime.timezone(datetime.timedelta(seconds=10800))),
                    'value': 'WAITING'}}
    """
    user: "User" = fields.ForeignKeyField("models.User", on_delete=fields.CASCADE, related_name="invoice_qiwis")
    comment = fields.CharField(255, null=True)

    async def check_payment(self, merchant: Merchant) -> bool:
        return await merchant.is_paid(self.invoice_id)

    @classmethod
    async def create_invoice(
            cls,
            merchant: Merchant,
            user: User,
            subscription_template: SubscriptionTemplate,
            amount: int | float | str,
            comment: str = None,
            email: str = None,
    ) -> Self:
        bill: Bill = await merchant.create_invoice(
            amount=amount,
            description=comment,
        )
        logger.info(f"InvoiceQiwi created [{user}][{bill.id}] {bill.pay_url}")
        created_invoice = await cls.create(
            amount=bill.amount.value,
            currency=bill.amount.currency,
            invoice_id=bill.id,
            pay_url=bill.pay_url,

            user=user,
            subscription_template=subscription_template,
            email=email,
        )
        logger.info(f"InvoiceQiwi created [{user.id}][{created_invoice.invoice_id}] {created_invoice.pay_url}")
        return created_invoice
