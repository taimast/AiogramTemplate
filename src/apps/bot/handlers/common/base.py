from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram import Bot, F, Router, types
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import User as TgUser

from src.apps.bot.commands.bot_commands import BaseCommands
from src.apps.bot.keyboards.common import common_kbs

if TYPE_CHECKING:
    from src.locales.stubs.ru.stub import TranslatorRunner

on = Router(name=__name__)


@on.message(CommandStart(deep_link=True))
async def deep_start(
    msg: types.Message,
    bot: Bot,
    command: CommandObject,
    l10n: TranslatorRunner,
    state: FSMContext,
):
    """Deep link start handler"""
    if command.args:
        referrer_id = int(command.args)
        # if user.set_referrer(referrer_id):
        #     await session.commit()

    await start(msg, l10n, state)


@on.message(Command(BaseCommands.START))
@on.message(F.text.startswith("«"))
@on.callback_query(F.data == "start")
async def start(
    msg: types.Message | types.CallbackQuery,
    l10n: TranslatorRunner,
    state: FSMContext,
    event_from_user: TgUser,
):
    await state.clear()
    if isinstance(msg, types.CallbackQuery):
        assert isinstance(msg.message, types.Message), "msg.message is not a Message"
        msg = msg.message

    assert msg.from_user, "msg.from_user is None"

    sm = await msg.answer(
        # l10n.start(name=msg.from_user.full_name),
        event_from_user.mention_html(),
        reply_markup=common_kbs.inline_start(),
    )
    # await msg.bot.send_message(
    #     "@taimastSan",
    #     f"{event_from_user.mention_html(name="XB")} брателла",
    # )
    # await msg.react([ReactionTypeEmoji(emoji="👍")])
