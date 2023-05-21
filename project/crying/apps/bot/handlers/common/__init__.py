from aiogram import Router

from . import base, group, payment

router = Router(name="common")
router.include_routers(
    base.router,
    group.router,
    payment.router,
)
