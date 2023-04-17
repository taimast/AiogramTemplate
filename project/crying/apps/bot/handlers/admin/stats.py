from aiogram import Router, types
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext

from ...keyboards.admin import admin_kbs
from ...keyboards.common.common_kbs import md
from .....db.models import User

router = Router()


@router.callback_query(Text("stats"))
async def stats(call: types.CallbackQuery, state: FSMContext):
    # Количество юзеров и количество юзеров за сегодня. Использовать md
    users_count = await User.all().count()
    users_today_count = await User.today_count()
    await call.message.answer(
        f"Количество пользователей: {md.hcode(users_count)}\n"
        f"Количество пользователей за сегодня: {md.hcode(users_today_count)}\n",
        reply_markup=admin_kbs.admin_start()
    )
