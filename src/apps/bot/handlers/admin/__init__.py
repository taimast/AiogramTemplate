from aiogram import Router

from . import mailing, menu, moderator, stats, users

on = Router(name="admin")
on.include_routers(
    menu.on,
    mailing.on,
    stats.on,
    users.on,
    moderator.on,
)
