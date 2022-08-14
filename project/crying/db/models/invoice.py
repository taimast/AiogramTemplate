import datetime
import typing
from abc import abstractmethod

from loguru import logger
from tortoise import fields, models
from tortoise.transactions import atomic

from project.crying.config import config, TIME_ZONE
from project.crying.config.config import PAYMENT_LIFETIME
from project.crying.config.yookassa_models import YooPayment
from .base import TimestampMixin
from .subscription import SubscriptionTemplate

if typing.TYPE_CHECKING:
    from .user import User

__all__ = ("AbstractInvoice", "InvoiceCrypto", "InvoiceQiwi", "InvoiceYooKassa")


class AbstractInvoice(TimestampMixin, models.Model):
    """Абстрактный класс для создания счета"""

    subscription_template: SubscriptionTemplate = fields.ForeignKeyField(
        "models.SubscriptionTemplate", null=True, on_delete=fields.SET_NULL
    )
    user: 'User' = fields.ForeignKeyField("models.User", on_delete=fields.CASCADE)
    currency = fields.CharField(5, default="RUB", description="RUB")
    amount = fields.DecimalField(17, 7)
    invoice_id = fields.CharField(50, index=True)
    expire_at = fields.DatetimeField(
        default=lambda: datetime.datetime.now(TIME_ZONE) + datetime.timedelta(minutes=PAYMENT_LIFETIME))
    email = fields.CharField(20, null=True)
    pay_url = fields.CharField(255)
    is_paid = fields.BooleanField(default=False)

    class Meta:
        abstract = True

    @atomic()
    async def successfully_paid(self):
        await self.fetch_related("user__subscription", "subscription_template")
        self.user.subscription.title = self.subscription_template.title
        self.user.subscription.duration += self.subscription_template.duration
        self.user.subscription.price = self.subscription_template.price
        self.is_paid = True
        await self.user.subscription.save(update_fields=["title", "duration", "price"])
        await self.save(update_fields=["is_paid"])

    @abstractmethod
    async def check_payment(self) -> bool:
        """"""

    @classmethod
    async def create_invoice(cls, **kwargs):
        pass


class InvoiceCrypto(AbstractInvoice):
    """
    for create:
        amount
        shop_id
        order_id
        email
        currency

    result:
        {'status': 'success',
        'pay_url': 'https://cryptocloud.plus/pay/4N8RWT',
        'currency': 'BTC',
        'invoice_id': '4N8RWT',
        'amount': 3e-06,
        'amount_usd': 0.1170788818966779}
    check result:
        {'status': 'success', 'status_invoice': 'created'}
        {'status': 'success', 'status_invoice': 'paid'}
    checked time:
        7-10 m
    """

    user: "User" = fields.ForeignKeyField("models.User", on_delete=fields.CASCADE, related_name="invoice_cryptos")
    shop_id = fields.CharField(50, default=config.payment.cryptocloud.shop_id)
    currency = fields.CharField(5, default="RUB", description="USD, RUB, EUR, GBP")
    order_id = fields.CharField(50, null=True, description="Custom product ID")

    async def check_payment(self) -> bool:
        return await config.merchants.crypto_cloud.is_paid(self.invoice_id)

    @classmethod
    async def create_invoice(
            cls,
            user: "User",
            subscription_template: SubscriptionTemplate,
            amount: int | float | str,
            currency="RUB",
            email: str = None,
            order_id: str = None,
    ) -> "InvoiceCrypto":
        data = await config.merchants.crypto_cloud.create_invoice(
            amount=amount,
            currency=currency,
            order_id=order_id,
            email=email,
        )
        created_invoice = await cls.create(
            amount=amount,
            currency=currency,
            order_id=order_id,
            email=email,
            invoice_id=data["invoice_id"],
            pay_url=data["pay_url"],
            user=user,
            subscription_template=subscription_template,
        )

        logger.info(f"InvoiceCrypto created [{user.id}][{created_invoice.invoice_id}] {created_invoice.pay_url}")
        return created_invoice


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

    async def check_payment(self) -> bool:
        return await config.merchants.qiwi.is_paid(self.invoice_id)

    @classmethod
    async def create_invoice(
            cls,
            user: "User",
            subscription_template: SubscriptionTemplate,
            amount: int | float | str,
            comment: str = None,
            email: str = None,
            lifetime: int = 30,
    ) -> "InvoiceQiwi":
        bill = await config.merchants.qiwi.create_invoice(
            amount=amount,
            description=comment,
        )
        logger.info(f"InvoiceQiwi created [{user}][{bill.id}] {bill.pay_url}")
        return await cls.create(
            **bill.dict(exclude={"id", "amount"}),
            user=user,
            subscription_template=subscription_template,
            amount=bill.amount.value,
            invoice_id=bill.id,
            email=email,
        )


class InvoiceYooKassa(AbstractInvoice):
    """
    {'id': '2a60ca77-000f-5000-a000-16cf4119f15e', 'status': 'pending', 'amount': {'value': '1.00',
                                                                                   'currency': 'RUB'},
    'description': 'Текстовый', 'recipient': {'account_id': '878719', 'gateway_id': '1934486'},
    'created_at': '2022-07-13T12:12:39.501Z',
    'confirmation': {'type': 'redirect',
                     'confirmation_url': 'https://yoomoney.ru/checkout/payments/v2/contract?orderId=2a60ca77-000f-5000-a000-16cf4119f15e'},
    'test': False, 'paid': False, 'refundable': False, 'metadata': {}}
    """

    user: "User" = fields.ForeignKeyField("models.User", on_delete=fields.CASCADE, related_name="invoice_yookassas")
    comment = fields.CharField(255, null=True)

    async def check_payment(self) -> bool:
        return await config.merchants.yookassa.is_paid(self.invoice_id)

    # todo 5/22/2022 3:46 PM taima: сделать для других валют

    @classmethod
    async def create_invoice(
            cls,
            user: "User",
            subscription_template: SubscriptionTemplate,
            amount: int | float | str,
            comment: str = None,
            email: str = None,
            lifetime: int = 30,
    ) -> "InvoiceYooKassa":
        yoo_payment: YooPayment = await config.merchants.yookassa.create_invoice(
            amount=amount,
            description=comment,
        )
        logger.info(f"InvoiceYooKassa created [{user}][{yoo_payment.id}] {yoo_payment.confirmation.confirmation_url}")
        return await cls.create(
            user=user,
            subscription_template=subscription_template,
            amount=yoo_payment.amount.value,
            comment=comment,
            invoice_id=yoo_payment.id,
            pay_url=yoo_payment.confirmation.confirmation_url,
            email=email,
        )
