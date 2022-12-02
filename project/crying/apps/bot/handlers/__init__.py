from aiogram import Dispatcher, Router

from . import common
from .errors import errors


def register_routers(dp: Dispatcher):
    router = Router()
    router.include_router(common.router)
    router.include_router(errors.router)
    dp.include_router(router)
