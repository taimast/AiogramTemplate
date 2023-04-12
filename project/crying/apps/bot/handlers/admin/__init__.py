from aiogram import Dispatcher, Router, F

from . import menu, mailing, stats

router = Router(name="admin")


def register_admin_routers(dp: Dispatcher, admins: list[int]):
    router.message.filter(F.from_user.id.in_(admins))
    router.callback_query.filter(F.from_user.id.in_(admins))
    router.include_router(menu.router)
    router.include_router(mailing.router)
    router.include_router(stats.router)
    dp.include_router(router)
