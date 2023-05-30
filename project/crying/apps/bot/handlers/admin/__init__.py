from aiogram import Router

from . import menu, mailing, stats, users

router = Router(name="admin")

router.include_routers(
    menu.router,
    mailing.router,
    stats.router,
    users.router
)
