from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram import Router, types, F, Bot
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import ReactionTypeEmoji
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.bot.commands.bot_commands import BaseCommands
from src.apps.bot.keyboards.common import common_kbs
from src.db.models import User

if TYPE_CHECKING:
    from src.locales.stubs.ru.stub import TranslatorRunner

on = Router(name=__name__)


@on.message(CommandStart(deep_link=True))
async def deep_start(
        msg: types.Message,
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
    await start(msg, session, l10n, state)


@on.message(Command(BaseCommands.START))
@on.message(F.text.startswith("«"))
@on.callback_query(F.data == "start")
async def start(
        msg: types.Message | types.CallbackQuery,
        session: AsyncSession,
        l10n: TranslatorRunner,
        state: FSMContext
):
    await state.clear()
    if isinstance(msg, types.CallbackQuery):
        msg = msg.message
    sm = await msg.answer(
        l10n.start(name=msg.from_user.full_name),
        reply_markup=common_kbs.inline_start()
    )
    await msg.react([ReactionTypeEmoji(emoji="👍")])
