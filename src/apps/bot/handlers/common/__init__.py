from aiogram import Router

from . import base, group, payment

on = Router(name="common")
on.include_routers(
    base.on,
    # group.on,
    # payment.on,
)
