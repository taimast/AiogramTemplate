from aiogram import Router, types
from aiogram.filters import StateFilter, Command, Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from project.crying.apps.bot.markups.admin import admin_markups

router = Router()



async def admin_start(message: types.CallbackQuery | types.Message, state: FSMContext):
    await state.clear()
    if isinstance(message, types.CallbackQuery):
        message = message.message
    await message.answer(f"Админ меню", reply_markup=admin_markups.admin_start())


def register_admin(dp: Router):
    dp.include_router(router)

    callback = router.callback_query.register
    message = router.message.register

    message(admin_start, Command(commands="admin"), StateFilter("*"))
    callback(admin_start, Text("admin"), StateFilter("*"))
