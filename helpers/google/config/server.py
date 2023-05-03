import asyncio
from dataclasses import dataclass
from enum import Enum
from functools import partial
from typing import Self

from aiohttp import web
from fluentogram import TranslatorHub
from loguru import logger
from shop_bot.apps.bot.utils.cart import CartManager
from shop_bot.config import Bot
from shop_bot.db.models import Order
from shop_bot.db.models.shop.order import OrderStatus


class Field(int, Enum):
    """Field"""
    STATUS = 1
    COMMENT = 8


@dataclass
class CellUpdate:
    """Cell update"""
    row: int
    column: str
    field: Field
    value: str | None = None
    old_value: str | None = None

    @classmethod
    def build(cls, cell: str, value: str = None, old_value: str = None) -> Self | None:
        """Build cell update"""
        if ":" in cell:
            return None

        if cell.startswith("B"):
            field = Field.STATUS
        elif cell.startswith("I"):
            field = Field.COMMENT
        else:
            return None
        return cls(
            row=int(cell[1:]),
            column=cell[0],
            field=field,
            value=value,
            old_value=old_value,
        )


async def handle(bot: Bot, cart_manager: CartManager, translator_hub: TranslatorHub, request: web.Request):
    """Handle request"""
    data: dict[str] = await request.json()
    logger.info(data)
    update = CellUpdate.build(**data)
    logger.info(update)
    try:
        if update is not None:
            order = await Order.get_or_none(sheet_id=update.row).select_related("user")
            if order is not None:
                card = cart_manager.get_cart(order.user.id)
                l10n = translator_hub.get_translator_by_locale(order.user.locale)
                if update.field == Field.STATUS:
                    await order.update(status=OrderStatus(update.value))
                    logger.info(f"Order {order.id} status updated to {update.value}")
                else:  # update.field == Field.COMMENT:
                    await order.update(user_comment=update.value or "")
                    logger.info(f"Order {order.id} comment updated to {update.value}")
                await card.edit_order_message(bot, order.id, order.to_history(l10n=l10n))
    except Exception as e:
        logger.warning(e)
    return web.Response()


async def start_trigger_server(bot: Bot, cart_manager: CartManager, translator_hub: TranslatorHub):
    """Start trigger server"""
    app = web.Application()
    runner = web.AppRunner(app)
    app.router.add_route("post", "/", partial(handle, bot, cart_manager, translator_hub))
    await runner.setup()
    site = web.TCPSite(
        runner,
        "0.0.0.0",
        8001,
    )
    await site.start()
    logger.info("Сервер запущен")
    # await asyncio.Future()


async def main():
    """Main function"""
    logger.info("Запуск сервера")
    await start_trigger_server()


if __name__ == '__main__':
    asyncio.run(main())
