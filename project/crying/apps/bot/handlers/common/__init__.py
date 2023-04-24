from aiogram import Router

from . import base, group

router = Router(name="common")
router.include_routers(
    base.router,
    group.router,
)
