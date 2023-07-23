from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.utils import markdown as md
from sqlalchemy.ext.asyncio import AsyncSession

from ...keyboards.admin import admin_kbs
from .....db.models import User

router = Router()


@router.callback_query(F.data == "stats")
async def stats(call: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    # Количество юзеров и количество юзеров за сегодня. Использовать md
    users_count = await User.count(session)
    users_today_count = await User.today_count(session)
    await call.message.answer(
        f"Количество пользователей: {md.hcode(users_count)}\n"
        f"Количество пользователей за сегодня: {md.hcode(users_today_count)}\n",
        reply_markup=admin_kbs.admin_start()
    )
