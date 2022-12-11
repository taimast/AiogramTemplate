from aiogram import Dispatcher, Router
from . import base

router = Router(name="common")
router.include_router(base.router)
