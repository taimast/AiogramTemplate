from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram import Router, types, Bot, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from aiogram.utils import markdown as md
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from ....callback_data.connect import ConnectCallback, ConnectAction
from ....commands.bot_commands import BaseCommands
from ....filters.is_connect import IsConnectedFilter
from ....keyboards.common import connect_kbs, helper_kbs
from ......config import Settings
from ......db.models import User

if TYPE_CHECKING:
    from ......locales.stubs.ru.stub import TranslatorRunner

on = Router(name=__name__)


async def disconnect_user(bot: Bot, user: User, l10n: TranslatorRunner):
    await user.awaitable_attrs.connected_user
    if not user.connected_user:
        return
    connected_user = user.connected_user
    await user.disconnect()
    if connected_user:
        try:
            await bot.send_message(connected_user.id, "...", reply_markup=ReplyKeyboardRemove())
            await bot.send_message(connected_user.id, l10n.conversation.end(), reply_markup=helper_kbs.custom_back_kb())
        except Exception as e:
            logger.warning(e)
        try:
            await bot.send_message(user.id, "...", reply_markup=ReplyKeyboardRemove())
            await bot.send_message(user.id, l10n.conversation.end(), reply_markup=helper_kbs.custom_back_kb())
        except Exception as e:
            logger.warning(e)


@on.message(F.text.startswith("☑️"))
async def end_conversation(
        message: types.Message,
        bot: Bot,
        user: User,
        l10n: TranslatorRunner,
        session: AsyncSession,
        state: FSMContext
):
    await state.clear()
    await disconnect_user(bot, user, l10n)
    await session.commit()


@on.message(IsConnectedFilter(), Command(BaseCommands.START))
async def connected(
        msg: types.Message,
        bot: Bot,
        user: User,
        settings: Settings,
        l10n: TranslatorRunner,
        session: AsyncSession,
        state: FSMContext
):
    await state.clear()
    await disconnect_user(bot, user, l10n)
    await session.commit()


@on.message(IsConnectedFilter(), ~Command(BaseCommands.START))
async def connected(message: types.Message, bot: Bot, user: User, settings: Settings, l10n: TranslatorRunner):
    await user.awaitable_attrs.connected_user
    connected_user: User = user.connected_user
    # connected_is_admin = connected_user.id in settings.bot.admins
    if user.id not in settings.bot.admins:
        prefix = md.hbold(l10n.conversation.message_from_user(name=user.full_name))
    else:
        prefix = md.hbold(l10n.conversation.message_from_moderator())
    answer_text = message.text or message.caption or ""
    text = f"{prefix}\n\n{answer_text}"
    if message.photo:
        await bot.send_photo(
            connected_user.id,
            message.photo[-1].file_id,
            caption=text,
        )
    elif message.video:
        await bot.send_video(
            connected_user.id,
            message.video.file_id,
            caption=text,
        )
    elif message.voice:
        await bot.send_voice(
            connected_user.id,
            message.voice.file_id,
            caption=text,
        )
    elif message.audio:
        await bot.send_audio(
            connected_user.id,
            message.audio.file_id,
            caption=text,
        )
    elif message.document:
        await bot.send_document(
            connected_user.id,
            message.document.file_id,
            caption=text,
        )
    else:
        await bot.send_message(
            connected_user.id,
            text,
        )

    # await bot.send_message(
    #     connected_user.id, f"{prefix}\n\n{message.text}",
    # )


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
        md.hbold(l10n.conversation.moderator.connected(name=connected_user.full_name)),
        reply_markup=connect_kbs.disconnect(l10n),
    )
    await bot.send_message(
        connected_user.id,
        md.hbold(l10n.conversation.user.connected()),
        reply_markup=connect_kbs.disconnect(l10n),
    )


@on.callback_query(ConnectCallback.filter(F.action == ConnectAction.CONNECT))
async def connect(
        call: types.CallbackQuery,
        session: AsyncSession,
        bot: Bot,
        user: User,
        callback_data: ConnectCallback,
        settings: Settings,
        l10n: TranslatorRunner
):
    await call.answer()

    connected_user: User = await session.get(User, callback_data.user_id)
    await connected_user.awaitable_attrs.connected_user
    if connected_user.connected_user and not callback_data.force:
        await call.message.answer(
            md.hbold(l10n.conversation.connect.already_connected(name=connected_user.full_name)),
            reply_markup=None
        )
        return
    await _connect(bot, user, connected_user, l10n)
    await session.commit()


@on.message(F.text.startswith("🗣️"))
async def connect(message: types.Message, bot: Bot, user: User, settings: Settings, l10n: TranslatorRunner):
    await message.answer(l10n.conversation.connect(), reply_markup=connect_kbs.disconnect(l10n))
    for admin in settings.bot.admins:
        try:
            await bot.send_message(
                admin, md.hbold(l10n.conversation.connect_request(name=user.full_name)),
                reply_markup=connect_kbs.connect(user.id, l10n),
            )
        except Exception as e:
            logger.warning(e)
