from aiogram import F, Router

from . import mailing, menu, moderator, stats, users

on = Router(name="admin")
on.message.filter(F.chat.type == "private")

on.include_routers(
    menu.on,
    mailing.on,
    stats.on,
    users.on,
    moderator.on,
)
