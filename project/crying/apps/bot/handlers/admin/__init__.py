from aiogram import Dispatcher, Router, F

from project.crying.config.config import Settings
from .admin_menu import register_admin

router = Router()


def register_admin_handlers(dp: Dispatcher, admins: list[int]):
    router.message.filter(F.from_user.id.in_(admins))
    router.callback_query.filter(F.from_user.id.in_(admins))
    register_admin(router)
    dp.include_router(router)
