from typing import Callable

from aiogram import Router, flags, types
from aiogram.fsm.context import FSMContext
from aiogram.utils import markdown as md
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.bot.callback_data.admin import AdminCallback
from src.apps.bot.filters.moderator_permission import ModeratorPermissionFilter
from src.apps.bot.keyboards.admin import admin_kbs
from src.apps.bot.keyboards.common import helper_kbs
from src.config import Settings
from src.db.models import User
from src.db.models.user.light import LightUser

on = Router(name=__name__)


@on.callback_query(AdminCallback.filter_stats_menu())
async def stats_menu(
    call: types.CallbackQuery,
    edit,
    light_user: LightUser,
    settings: Settings,
    state: FSMContext,
    l10n,
):
    await edit(
        l10n.get("admin-stats-menu-select"),
        reply_markup=admin_kbs.stats(light_user.id, settings.bot, l10n),
    )


@on.callback_query(
    AdminCallback.filter_common_stats(),
    ModeratorPermissionFilter(),
)
@flags.session
async def common_stats(
    call: types.CallbackQuery,
    edit: Callable,
    session: AsyncSession,
    settings: Settings,
    state: FSMContext,
    l10n,
):
    users_count = await User.count(session)
    users_today_count = await User.today_count(session)
    premium_users_count = await User.count(session, User.is_premium.isnot(None))

    await edit(
        l10n.get(
            "admin-stats-menu-common_stats",
            users_count=md.hcode(users_count),
            premium_users_count=md.hcode(premium_users_count),
            users_today_count=md.hcode(users_today_count),
        ),
        reply_markup=helper_kbs.custom_back_kb(cd=AdminCallback.start_menu()),
    )
