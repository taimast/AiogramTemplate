from aiogram import Dispatcher, Router
from . import base

router = Router()
router.include_router(base.router)
