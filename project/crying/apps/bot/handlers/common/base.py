from aiogram import Router, types
from aiogram.filters import StateFilter, Command, Text
from aiogram.fsm.context import FSMContext

router = Router()


@router.message(Command("start"), StateFilter("*"))
@router.callback_query(Text("start"), StateFilter("*"))
async def start(message: types.Message | types.CallbackQuery, state: FSMContext):
    await state.clear()
    if isinstance(message, types.CallbackQuery):
        message = message.message
    await message.answer("Стартовое меню!")


