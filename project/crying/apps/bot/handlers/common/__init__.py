from aiogram import Router

from . import base, group

router = Router(name="common")
router.include_router(base.router)
router.include_router(group.router)
