from aiogram import Router, types
from aiogram.filters import StateFilter, Command, Text
from aiogram.fsm.context import FSMContext

from project.crying.apps.bot.keyboards.admin import admin_markups

router = Router()


@router.callback_query(Text("admin"), StateFilter("*"))
@router.message(Command("admin"))
async def admin_start(message: types.CallbackQuery | types.Message, state: FSMContext):
    await state.clear()
    if isinstance(message, types.CallbackQuery):
        message = message.message
    await message.answer(f"Админ меню", reply_markup=admin_markups.admin_start())

