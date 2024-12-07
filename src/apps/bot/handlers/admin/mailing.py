from __future__ import annotations

import asyncio
import csv
import typing

from aiogram import Bot, F, Router, flags, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from fluentogram import TranslatorRunner
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.bot.types.message import (
    NonEmptyMessageCallbackQuery,
    NonEmptyTextMessage,
)
from src.apps.bot.types.user import TgUser

from .....config import Settings
from .....db.models import User
from .....db.models.user import Locale
from .....utils.mailing import Mailing
from ...callback_data.admin import AdminCallback
from ...keyboards.admin import admin_kbs
from ...keyboards.common import helper_kbs

on = Router(name=__name__)


@on.callback_query(AdminCallback.filter_mailing())
async def mailing_header(
    call: types.CallbackQuery,
    edit: typing.Callable,
    settings: Settings,
    l10n: TranslatorRunner,
    state: FSMContext,
):
    await edit(
        l10n.get("admin-mailing-header"),
        reply_markup=admin_kbs.mailing(l10n),
    )


@on.callback_query(AdminCallback.filter_start_mailing())
async def mailing_start(
    call: types.CallbackQuery,
    edit: typing.Callable,
    settings: Settings,
    l10n: TranslatorRunner,
    state: FSMContext,
):
    await edit(
        l10n.get("admin-mailing-select_language"),
        reply_markup=admin_kbs.mailing_language(l10n),
    )

    await state.set_state("choose_language")


@on.callback_query(StateFilter("choose_language"))
async def mailing(
    call: NonEmptyMessageCallbackQuery,
    edit: typing.Callable,
    settings: Settings,
    state: FSMContext,
    l10n: TranslatorRunner,
):
    locale_str = call.data.split(":")[-1]
    if locale_str == "all":
        await state.update_data(locale=None)
    elif locale_str == "private":
        await state.update_data(locale="private")
        await edit(
            l10n.get("admin-mailing-private_users_prompt"),
            reply_markup=helper_kbs.custom_back_kb(cd="admin"),
        )
        await state.set_state("private_mailing_users")
        return
    else:
        locale = Locale(locale_str)
        await state.update_data(locale=locale)
    await edit(
        l10n.get("admin-mailing-message_prompt"),
        reply_markup=helper_kbs.custom_back_kb(cd="admin"),
    )

    await state.set_state("start_mailing")


@on.message(StateFilter("private_mailing_users"))
async def private_mailing_users(
    message: NonEmptyTextMessage,
    edit: typing.Callable,
    state: FSMContext,
    l10n: TranslatorRunner,
):
    if message.text:
        text = message.text
        user_data = text.split("\n")
        prepare_destinations = []
        for user in user_data:
            user_data = user.split(",")
            prepare_destinations.append(user_data[0].strip())
    else:
        file = message.document
        if not file:
            await message.answer(l10n.get("admin-mailing-empty_message"))
            return
        data_file: typing.BinaryIO | None = await message.bot.download(file)
        assert data_file is not None, "data_file is None"

        csv_reader = csv.reader(data_file.read().decode("utf-8").splitlines())
        prepare_destinations = []
        for row in csv_reader:
            prepare_destinations.append(row[0].strip())

    await state.update_data(private_mailing_users=prepare_destinations)

    await edit(
        l10n.get("admin-mailing-message_prompt"),
        reply_markup=helper_kbs.custom_back_kb(cd="admin"),
    )
    await state.set_state("start_mailing")


@on.message(StateFilter("start_mailing"))
async def add_buttons(
    message: types.Message,
    edit: typing.Callable,
    state: FSMContext,
    l10n: TranslatorRunner,
):
    await state.update_data(send_message=message)
    await edit(
        l10n.get("admin-mailing-buttons_prompt"),
        reply_markup=admin_kbs.add_buttons(l10n),
    )
    await state.set_state("pre-mailing")


@on.message(StateFilter("pre-mailing"))
@on.callback_query(F.data == "send_mailing")
async def mailing_send(
    message: NonEmptyTextMessage,
    bot: Bot,
    state: FSMContext,
    l10n: TranslatorRunner,
):
    data = await state.get_data()
    send_message: types.Message = data["send_message"]

    if isinstance(message, types.CallbackQuery):
        send_reply_markup = send_message.reply_markup

        message = message.message  # type: ignore
    else:
        send_reply_markup = admin_kbs.created_buttons(message.text)

    await state.update_data(send_reply_markup=send_reply_markup, send_message=send_message)

    await message.bot.copy_message(
        chat_id=message.chat.id,
        from_chat_id=message.chat.id,
        message_id=send_message.message_id,
        reply_markup=send_reply_markup,
    )

    await message.answer(
        l10n.get("admin-mailing-confirm_prompt"),
        reply_markup=admin_kbs.confirm_mailing(l10n),
    )


@on.callback_query(F.data == "confirm_mailing")
@flags.session
async def mailing_send_confirm(
    call: NonEmptyMessageCallbackQuery,
    session: AsyncSession,
    bot: Bot,
    state: FSMContext,
    l10n: TranslatorRunner,
):
    data = await state.get_data()
    send_message: types.Message = data["send_message"]
    send_reply_markup = data.get("send_reply_markup")
    message = call.message

    try:
        data = await state.get_data()
        locale = data.get("locale")
        interval = data.get("interval", 0.4)
        mailing_obj = Mailing(
            update_interval=60,
            send_interval=interval,
            cancel_markup=admin_kbs.mailing_cancel(l10n),
        )
        await mailing_obj.init_status_message(message)
        mailing_status_task = asyncio.create_task(mailing_obj.live_updating_status())

        if locale == "private":
            private_mailing_users = data["private_mailing_users"]
            users = await User.filter(session, User.username.in_(private_mailing_users))
        elif locale:
            users = await User.filter(session, User.language_code == locale)
        else:
            users = await User.all(session)

        user_ids = [user.id for user in users]
        mailing_task = asyncio.create_task(
            mailing_obj.send_notifications(bot, user_ids, send_message, send_reply_markup)
        )
        await state.update_data(mailing_task=mailing_task, mailing_obj=mailing_obj)
        cancelled = False
        try:
            await mailing_task
        except asyncio.CancelledError:
            cancelled = True
        finally:
            mailing_status_task.cancel()

        try:
            await mailing_status_task
        except asyncio.CancelledError:
            pass

        if cancelled:
            await mailing_obj.cancel()
        else:
            await mailing_obj.done()
        Mailing.mailings.append(mailing_obj)
        await message.answer(l10n.get("admin-mailing-done"), reply_markup=admin_kbs.back())

    except Exception as e:
        logger.error(f"Error while sending mailing: {e}")
        await message.answer(l10n.get("admin-mailing-error", error=str(e)), parse_mode=None)

    await state.clear()


@on.callback_query(AdminCallback.filter_retract_last_mailing())
async def retract_last_mailing(
    call: NonEmptyMessageCallbackQuery,
    settings: Settings,
    bot: Bot,
    event_from_user: TgUser,
    l10n: TranslatorRunner,
):
    mailing_obj = Mailing.get_last()
    if mailing_obj:
        mailing_status_task = asyncio.create_task(mailing_obj.live_updating_status())
        mailing_task = asyncio.create_task(mailing_obj.retract(bot))
        cancelled = False
        try:
            await mailing_task
        except asyncio.CancelledError:
            cancelled = True
        finally:
            mailing_status_task.cancel()

        try:
            await mailing_status_task
        except asyncio.CancelledError:
            pass

        if cancelled:
            await mailing_obj.cancel()
        else:
            await mailing_obj.retracted_status()

        Mailing.mailings.pop()
        await call.message.edit_text(
            l10n.get("admin-mailing-retracted"),
            reply_markup=admin_kbs.admin_start(
                event_from_user.id,
                settings.bot,
                l10n,
            ),
        )
    else:
        await call.message.answer(l10n.get("admin-mailing-no_last"))


@on.callback_query(AdminCallback.filter_mailing_cancel())
async def mailing_cancel(
    call: NonEmptyMessageCallbackQuery,
    state: FSMContext,
    l10n: TranslatorRunner,
):
    data = await state.get_data()
    mailing_task: asyncio.Task | None = data.get("mailing_task")
    confirm_cancel: bool = data.get("confirm_cancel", False)

    if not confirm_cancel:
        await call.answer(l10n.get("admin-mailing-confirm_cancel"))
        await state.update_data(confirm_cancel=True)
        return

    if mailing_task:
        mailing_task.cancel()
        await call.message.answer(l10n.get("admin-mailing-cancelling"))
    else:
        await call.answer(l10n.get("admin-mailing-no_active"))
    await state.clear()


@on.callback_query(F.data == "update_mailing_stats")
async def mailing_update_stats(
    call: types.CallbackQuery,
    state: FSMContext,
    l10n: TranslatorRunner,
):
    data = await state.get_data()
    mailing_obj: Mailing | None = data.get("mailing_obj")
    if mailing_obj:
        await mailing_obj.update_status()
    else:
        await call.answer(l10n.get("admin-mailing-no_active"))
