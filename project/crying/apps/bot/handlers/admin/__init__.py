from aiogram import Router

from . import menu, mailing, stats

router = Router(name="admin")

router.include_routers(
    menu.router,
    mailing.router,
    stats.router,
)
