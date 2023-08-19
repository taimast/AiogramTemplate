from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from project.crying.apps.bot.commands.bot_commands import BaseCommands
from project.crying.apps.bot.keyboards.common import common_kbs

if TYPE_CHECKING:
    from project.crying.locales.stubs.ru.stub import TranslatorRunner

router = Router()


@router.message(Command(BaseCommands.START))
@router.message(F.text.startswith("«"))
@router.callback_query(F.data == "start")
async def start(
        message: types.Message | types.CallbackQuery,
        session: AsyncSession,
        l10n: TranslatorRunner,
        state: FSMContext
):
    await state.clear()
    if isinstance(message, types.CallbackQuery):
        message = message.message
    await message.answer(
        l10n.start(name=message.from_user.full_name),
        reply_markup=common_kbs.inline_start()
    )
