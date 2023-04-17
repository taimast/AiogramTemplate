from aiogram import Router, types
from aiogram.filters import Command, Text
from aiogram.fsm.context import FSMContext

from ...commands.bot_commands import AdminCommands
from ...keyboards.admin import admin_kbs

router = Router()


@router.callback_query(Text("admin"))
@router.message(Command(AdminCommands.ADMIN))
async def admin_start(message: types.CallbackQuery | types.Message, state: FSMContext):
    await state.clear()
    if isinstance(message, types.CallbackQuery):
        message = message.message
    await message.answer(f"Админ меню", reply_markup=admin_kbs.admin_start())
