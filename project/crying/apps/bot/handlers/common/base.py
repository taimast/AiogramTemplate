from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram import Router, types, F, Bot
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.utils.media_group import MediaGroupBuilder
from sqlalchemy.ext.asyncio import AsyncSession


from project.crying.apps.bot.commands.bot_commands import BaseCommands
from project.crying.apps.bot.keyboards.common import common_kbs
from project.crying.db.models import User

if TYPE_CHECKING:
    from project.crying.locales.stubs.ru.stub import TranslatorRunner

router = Router()

@router.message(CommandStart(deep_link=True))
async def deep_start(
        message: types.Message,
        bot: Bot,
        command: CommandObject,
        session: AsyncSession,
        user: User,
        l10n: TranslatorRunner,
        state: FSMContext
):
    """ Deep link start handler """
    referrer_id = int(command.args)
    if user.set_referrer(referrer_id):
        await session.commit()
    await start(message, l10n, bot, state)

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

@router.callback_query()
async def media(call:types.CallbackQuery):
    group = MediaGroupBuilder()
    group.add_photo()
    group.build()