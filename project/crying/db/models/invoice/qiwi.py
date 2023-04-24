from __future__ import annotations

from typing import Self, TYPE_CHECKING

from glQiwiApi.qiwi.clients.p2p.types import Bill
from loguru import logger
from sqlalchemy import String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from .base import AbstractInvoice
from ..user import User

if TYPE_CHECKING:
    from ....apps.merchant.qiwi import Qiwi


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
    __tablename__ = 'invoices_qiwi'
    comment: Mapped[str | None] = mapped_column(String(255))

    @classmethod
    async def create_invoice(
            cls,
            session: AsyncSession,
            merchant: Qiwi,
            user: User,
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
            session=session,
            user=user,
            amount=bill.amount.value,
            currency=bill.amount.currency,
            invoice_id=bill.id,
            pay_url=bill.pay_url,
            email=email,
        )
        logger.info(f"InvoiceQiwi created [{user.id}][{created_invoice.invoice_id}] {created_invoice.pay_url}")
        return created_invoice
