from aiogram import Dispatcher, Router
from . import common_menu

router = Router()
router.include_router(common_menu.router)
