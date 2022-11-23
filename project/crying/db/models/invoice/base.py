import datetime

from tortoise import models, fields
from tortoise.transactions import atomic

from project.crying.config import TIME_ZONE
from project.crying.config.merchant.base import PAYMENT_LIFETIME

from project.crying.db.models import User
from project.crying.db.models.subscription import SubscriptionTemplate


class AbstractInvoice(models.Model):
    """Абстрактный класс для создания счета"""
    subscription_template: 'SubscriptionTemplate' = fields.ForeignKeyField(
        "models.SubscriptionTemplate", null=True, on_delete=fields.SET_NULL
    )
    user: User = fields.ForeignKeyField("models.User", on_delete=fields.CASCADE)
    currency = fields.CharField(5, default="RUB", description="RUB")
    amount = fields.DecimalField(17, 7)
    invoice_id = fields.CharField(50, index=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    expire_at = fields.DatetimeField(
        default=lambda: datetime.datetime.now(TIME_ZONE) + datetime.timedelta(seconds=PAYMENT_LIFETIME)
    )
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
        await self.user.subscription.save()
        await self.save(update_fields=["is_paid"])

    async def check_payment(self) -> bool:
        pass

    @classmethod
    async def create_invoice(cls, **kwargs):
        pass
