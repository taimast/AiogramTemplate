from aiogram import Dispatcher, Router, F

from project.crying.config.config import config
from .admin_menu import register_admin
from .bot_settings import register_bot_settings
from .channel_menu import register_channel
from .send_mail import register_send_mail
from .statistics_menu import register_statistics

router = Router()


def register_admin_handlers(dp: Dispatcher):
    router.message.filter(F.from_user.id.in_(config.bot.admins))
    router.callback_query.filter(F.from_user.id.in_(config.bot.admins))
    register_admin(router)
    register_channel(router)
    register_send_mail(router)
    register_bot_settings(router)
    register_statistics(router)
    dp.include_router(router)
