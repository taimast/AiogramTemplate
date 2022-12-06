from aiogram import Router, types
from aiogram.filters import StateFilter, Command, Text
from aiogram.fsm.context import FSMContext

from project.crying.apps.bot.commands.bot_commands import BotCommands

router = Router()


@router.message(Command(BotCommands.START), StateFilter("*"))
@router.callback_query(Text("start"), StateFilter("*"))
async def start(message: types.Message | types.CallbackQuery, state: FSMContext):
    await state.clear()
    if isinstance(message, types.CallbackQuery):
        message = message.message
    await message.answer("Стартовое меню!")

