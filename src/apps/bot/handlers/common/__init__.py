from aiogram import Router

from . import base, group, payment, connect

on = Router(name="common")
on.include_routers(
    group.on,

    base.on,
    payment.on,
)
