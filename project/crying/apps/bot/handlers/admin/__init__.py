from aiogram import Dispatcher, Router, F

from project.crying.config.config import config
from .admin_menu import register_admin

router = Router()


def register_admin_handlers(dp: Dispatcher):
    router.message.filter(F.from_user.id.in_(config.bot.admins))
    router.callback_query.filter(F.from_user.id.in_(config.bot.admins))
    register_admin(router)
    dp.include_router(router)
