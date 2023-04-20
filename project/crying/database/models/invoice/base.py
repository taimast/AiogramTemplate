import datetime
from enum import StrEnum
from typing import Self

from sqlalchemy import String, func
from sqlalchemy.orm import Mapped, mapped_column
from tortoise.transactions import atomic

from ..base import Base, TimestampMixin
from ..user import User
from ....apps.merchant.base import PAYMENT_LIFETIME, Merchant


class Currency(StrEnum):
    """Currency codes."""
    RUB = "RUB"
    USD = "USD"
    EUR = "EUR"


class Status(StrEnum):
    """Invoice status."""
    PENDING = "pending"
    SUCCESS = "success"
    EXPIRED = "expired"
    FAIL = "fail"


class AbstractInvoice(Base, TimestampMixin):
    __tablename__ = "invoices"
    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    # user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    # user: Mapped[User] = relationship(back_populates="invoices")
    currency: Mapped[Currency | None]
    amount: Mapped[float | None]
    expire_at: Mapped[datetime.datetime | None] = mapped_column(
        default=func.now() + datetime.timedelta(seconds=PAYMENT_LIFETIME))
    additional_info: Mapped[str | None] = mapped_column(String(255))
    pay_url: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[Status | None] = mapped_column(String(10), default=Status.PENDING)

    class Meta:
        abstract = True

    def __str__(self):
        return f"[{self.__class__.__name__}] {self.user} {self.amount} {self.currency}"

    @atomic()
    async def successfully_paid(self):
        """Успешная оплата"""
        await self.fetch_related("user__subscription", "subscription_template")
        self.user.subscription.title = self.subscription_template.title
        self.user.subscription.duration += self.subscription_template.duration
        self.user.subscription.price = self.subscription_template.price
        self.is_paid = True
        await self.user.subscription.save()
        await self.save(update_fields=["is_paid"])

    async def check_payment(self, merchant: Merchant) -> bool:
        """Проверка оплаты"""
        raise NotImplementedError

    @classmethod
    async def create_invoice(
            cls,
            merchant: Merchant,
            user: User,
            amount: int | float | str,
            **kwargs,
    ) -> Self:
        """Создание счета"""
        raise NotImplementedError
