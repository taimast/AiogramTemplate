from functools import lru_cache
from typing import Type

from ..apps.merchant.base import Merchant
from ..apps.merchant.group import MerchantGroup
from ..db.models import InvoiceCrypto, InvoiceQiwi, InvoiceYooKassa
from ..db.models.invoice import AbstractInvoice


@lru_cache
def get_merchant_invoice_class(
        merchant: Merchant,
        merchant_group: MerchantGroup | None
) -> Type[AbstractInvoice] | None:
    """Получение класса счета для мерчанта."""
    return get_merchants_invoice_classes(merchant_group).get(merchant)


@lru_cache
def get_merchants_invoice_classes(merchant_group: MerchantGroup | None) -> dict[Merchant, Type[AbstractInvoice]]:
    """Получение классов счетов для мерчантов."""
    # Получение всех активных заказов
    merchants_invoice_classes = {}
    if not merchant_group:
        return merchants_invoice_classes
    if merchant_group.qiwi:
        merchants_invoice_classes[merchant_group.qiwi] = InvoiceQiwi
    if merchant_group.yookassa:
        merchants_invoice_classes[merchant_group.yookassa] = InvoiceYooKassa
    if merchant_group.crypto_cloud:
        merchants_invoice_classes[merchant_group.crypto_cloud] = InvoiceCrypto
    return merchants_invoice_classes
