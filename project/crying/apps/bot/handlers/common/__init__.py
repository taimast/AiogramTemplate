from aiogram import Dispatcher, Router

from .common_menu import register_common


router = Router()


def register_common_handlers(dp: Dispatcher):
    register_common(router)
    dp.include_router(router)
