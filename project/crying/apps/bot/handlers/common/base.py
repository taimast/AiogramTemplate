from aiogram import Router, types
from aiogram.filters import StateFilter, Command, Text
from aiogram.fsm.context import FSMContext

from project.crying.apps.bot.commands.bot_commands import BaseCommands
from project.crying.apps.bot.middleware.l10n import FluentLocalization
from project.crying.db.models import User

router = Router()


@router.message(Command(BaseCommands.START))
@router.callback_query(Text("start"))
async def start(message: types.Message | types.CallbackQuery, user: User, l10n: FluentLocalization, state: FSMContext):
    await state.clear()
    if isinstance(message, types.CallbackQuery):
        message = message.message
    await message.answer(l10n("start", {"name": user.first_name}))
