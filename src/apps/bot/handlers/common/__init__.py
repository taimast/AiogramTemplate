from aiogram import F, Router

from . import base, connect, group, payment, support

private_router = Router(name="private")
private_router.message.filter(F.chat.type == "private")
private_router.include_routers(
    base.on,
    payment.on,
)
on = Router(name="common")

on.include_routers(
    private_router,
    support.on,
    group.on,
)
