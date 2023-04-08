from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram import Router, types, Bot, F
from aiogram.filters import Text, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from aiogram.utils import markdown as md

from ...callback_data.connect import ConnectCallback, Action
from ...filters.connect import IsConnectedFilter
from ...keyboards.common import common_kbs
from .....config import Settings
from .....db.models import User

if TYPE_CHECKING:
    from ...locales.stubs.ru.stub import TranslatorRunner

router = Router()


def get_chat_name(chat: User) -> str:
    if chat.first_name and chat.last_name:
        name = f"{chat.first_name} {chat.last_name}"
    elif chat.first_name:
        name = chat.first_name
    elif chat.last_name:
        name = chat.last_name
    elif chat.username:
        name = f"@{chat.username}"
    else:
        name = f"id{chat.id}"

    return f"{name} (@{chat.username})"


async def disconnect_user(bot: Bot, user: User, l10n: TranslatorRunner):
    if not user.is_connected:
        return
    await user.fetch_related("connected_user")
    connected_user = user.connected_user
    await user.disconnect()
    if connected_user:
        await bot.send_message(connected_user.id, "...", reply_markup=ReplyKeyboardRemove())
        await bot.send_message(connected_user.id, l10n.conversation.end(), reply_markup=common_kbs.custom_back())
        await bot.send_message(user.id, "...", reply_markup=ReplyKeyboardRemove())
        await bot.send_message(user.id, l10n.conversation.end(), reply_markup=common_kbs.custom_back())


@router.message(Text(startswith="☑️"))
async def end_conversation(message: types.Message, bot: Bot, user: User, l10n: TranslatorRunner, state: FSMContext):
    await state.clear()
    await disconnect_user(bot, user, l10n)


@router.message(IsConnectedFilter(), ~Command("start"))
async def connected(message: types.Message, bot: Bot, user: User, settings: Settings, l10n: TranslatorRunner):
    await user.fetch_related("connected_user")
    connected_user = user.connected_user
    # connected_is_admin = connected_user.id in settings.bot.admins
    if user.id not in settings.bot.admins:
        prefix = md.hbold(l10n.conversation.message_from_user(name=get_chat_name(user)))
    else:
        prefix = md.hbold(l10n.conversation.message_from_moderator())
    await bot.send_message(
        connected_user.id, f"{prefix}\n\n{message.text}",
    )


async def _connect(
        bot: Bot,
        user: User,
        connected_user: User,
        l10n: TranslatorRunner,
):
    await disconnect_user(bot, user, l10n)
    await disconnect_user(bot, connected_user, l10n)

    await user.connect(connected_user)
    await bot.send_message(
        user.id,
        md.hbold(l10n.conversation.moderator.connected(name=get_chat_name(connected_user))),
        reply_markup=common_kbs.disconnect(l10n),
    )
    await bot.send_message(
        connected_user.id,
        md.hbold(l10n.conversation.user.connected()),
        reply_markup=common_kbs.disconnect(l10n),
    )


@router.callback_query(ConnectCallback.filter(F.action == Action.connect))
async def connect(
        call: types.CallbackQuery,
        bot: Bot,
        user: User,
        callback_data: ConnectCallback,
        settings: Settings,
        l10n: TranslatorRunner
):
    await call.answer()
    connected_user = await User.get(id=callback_data.user_id)
    if connected_user.is_connected and not callback_data.force:
        await call.message.answer(
            md.hbold(l10n.conversation.connect.already_connected(name=get_chat_name(connected_user))),
            reply_markup=None
        )
        return
    await _connect(bot, user, connected_user, l10n)
