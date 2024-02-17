from aiogram import Router

from . import menu, mailing, stats, users

on = Router(name="admin")
on.include_routers(
    menu.on,
    mailing.on,
    stats.on,
    users.on
)
