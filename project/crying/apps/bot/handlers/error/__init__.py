from aiogram import Router

from . import errors

router = Router(name="error")
router.include_routers(
    errors.router,
)
