import datetime
from abc import abstractmethod
from enum import StrEnum
from typing import Self, TypeVar, Generic

from sqlalchemy import String, func, ForeignKey
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import TimestampMixin
from ..base.declarative import Base
from ..user import User
from ....apps.merchant.base import PAYMENT_LIFETIME, Merchant

MerchantType = TypeVar("MerchantType", bound=Merchant)


class Currency(StrEnum):
    """Currency codes."""
    USD = "USD"
    RUB = "RUB"
    EUR = "EUR"
    GBP = "GBP"
    USDT = "USDT"


class Status(StrEnum):
    """Invoice status."""
    PENDING = "pending"
    SUCCESS = "success"
    EXPIRED = "expired"
    FAIL = "fail"


class AbstractInvoice(Base, TimestampMixin, Generic[MerchantType]):
    __abstract__ = True
    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped[User] = relationship(back_populates="invoices")
    currency: Mapped[Currency | None]
    amount: Mapped[float | None]
    invoice_id: Mapped[str] = mapped_column(String(50), index=True)
    expire_at: Mapped[datetime.datetime | None] = mapped_column(
        server_default=func.now() + datetime.timedelta(seconds=PAYMENT_LIFETIME)
    )
    additional_info: Mapped[str | None] = mapped_column(String(255))
    pay_url: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[Status | None] = mapped_column(String(10), default=Status.PENDING)

    class Meta:
        abstract = True

    def __str__(self):
        return f"[{self.__class__.__name__}] {self.user} {self.amount} {self.currency}"

    # todo L1 TODO 22.04.2023 22:56 taima: Do successfully_paid and check_payment methods in one method
    async def successfully_paid(self):
        """Successful payment."""
        self.status = Status.SUCCESS

    @classmethod
    @abstractmethod
    async def create_invoice(
            cls,
            session: AsyncSession,
            merchant: MerchantType,
            user: User,
            amount: int | float | str,
            **kwargs,
    ) -> Self:
        """Create invoice."""
        raise NotImplementedError
