from __future__ import annotations

from typing import TYPE_CHECKING

from .helper_kbs import CustomInlineKeyboardBuilder
from ...commands.bot_commands import BaseCommands

if TYPE_CHECKING:
    from .....locales.stubs.ru.stub import TranslatorRunner


def payment_created(pay_url: str, l10n: TranslatorRunner):
    builder = CustomInlineKeyboardBuilder()
    builder.button(
        text=l10n.get("payment-button-pay"),
        url=pay_url
    )
    builder.button(
        text=l10n.get("payment-button-i_paid"),
        callback_data="i_paid"
    )
    builder.adjust(1)
    builder.add_start_back()
    return builder.as_markup()


def expired(l10n: TranslatorRunner):
    builder = CustomInlineKeyboardBuilder()
    builder.button(
        text=l10n.get("payment-button-extend"),
        callback_data=BaseCommands.PAYMENT.command
    )
    builder.adjust(1)
    builder.add_start_back()
    return builder.as_markup()
