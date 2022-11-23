from aiogram import Router, types
from aiogram.filters import StateFilter, Command, Text
from aiogram.fsm.context import FSMContext

from project.crying.db.models import User

router = Router()


async def start(message: types.Message | types.CallbackQuery, state: FSMContext):
    await state.clear()
    if isinstance(message, types.CallbackQuery):
        message = message.message
    await message.answer("Стартовое меню!")


def register_common(dp: Router):
    dp.include_router(router)

    callback = router.callback_query.register
    message = router.message.register

    # message(start,  StateFilter("*"))
    message(start, Command(commands="start"), StateFilter("*"))
    callback(start, Text("start"), StateFilter("*"))
