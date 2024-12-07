import asyncio
from typing import Callable, Iterable

import aiocsv
import aiofiles
from aiogram import F, Router, flags, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.utils import deep_linking
from cachetools import TTLCache
from fluentogram import TranslatorRunner
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.bot.callback_data.actions import UserAction
from src.apps.bot.callback_data.admin import AdminCallback
from src.apps.bot.callback_data.user import UserCallback
from src.apps.bot.filters.moderator_permission import ModeratorPermissionFilter
from src.apps.bot.keyboards.admin import admin_kbs
from src.apps.bot.keyboards.common import helper_kbs
from src.apps.bot.keyboards.common.helper_kbs import md
from src.apps.bot.types.message import NonEmptyMessageCallbackQuery, NonEmptyTextMessage
from src.apps.bot.types.user import TgUser
from src.config import MEDIA_DIR, Settings
from src.db.models import User
from src.db.models.user.light import LightUser
from src.db.persistence_session.manager import PersistenceSessionManager
from src.utils.message import split_sending_proper

on = Router(name=__name__)

EXCEL_LOCK = asyncio.Lock()
USERS_EXEL_FILE_ID_CACHE = TTLCache(maxsize=1024, ttl=60)


async def prepare_users_data_in_chunks(
    users_with_referrals: Iterable[tuple[User, int]],
    l10n: TranslatorRunner,
    file: str = "users.csv",
):
    # Добавляем заголовки
    headers = [
        l10n.get("admin-excel-field-id"),
        l10n.get("admin-excel-field-username"),
        l10n.get("admin-excel-field-language"),
        l10n.get("admin-excel-field-created_at"),
        l10n.get("admin-excel-field-tg_premium"),
        l10n.get("admin-excel-field-referral_count"),
    ]
    users_data = [
        [
            user.id,
            user.username,
            user.language_code,
            user.created_at,
            user.is_premium,
            referral_counts,
        ]
        for user, referral_counts in users_with_referrals
    ]

    # Сохраняем Excel файл
    csv_path = MEDIA_DIR / file
    async with aiofiles.open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = aiocsv.AsyncWriter(csvfile)
        await writer.writerow(headers)

        # Записываем данные пользователей
        for user_data in users_data:
            await writer.writerow(user_data)

    return csv_path


@on.callback_query(AdminCallback.filter_export_users(), ModeratorPermissionFilter())
@flags.session
async def export_users(
    call: NonEmptyMessageCallbackQuery,
    settings: Settings,
    session: AsyncSession,
    l10n: TranslatorRunner,
    state: FSMContext,
):
    await call.message.answer(l10n.get("admin-users-export"))
    users_with_referrals = await User.get_users_with_referral_counts(session)

    cache_key = "users.csv"

    async with EXCEL_LOCK:
        if excel_file_id := USERS_EXEL_FILE_ID_CACHE.get(cache_key):
            document = excel_file_id
        else:
            excel_path = await prepare_users_data_in_chunks(
                users_with_referrals,
                l10n,
                cache_key,
            )
            document = types.FSInputFile(excel_path)

    await state.clear()

    # Отправляем файл пользователю
    sm = await call.message.answer_document(
        document=document,
        caption=l10n.get("admin-users-export_done"),
    )
    USERS_EXEL_FILE_ID_CACHE[cache_key] = sm.document.file_id  # type: ignore


@on.callback_query(AdminCallback.filter_user_stats(), ModeratorPermissionFilter())
async def user_stats(
    call: types.CallbackQuery,
    edit: Callable,
    state: FSMContext,
    l10n: TranslatorRunner,
):
    await edit(l10n.get("admin-users-enter_id_username"), reply_markup=admin_kbs.back())
    await state.set_state("admin:user_stats")


@on.message(StateFilter("admin:user_stats"))
@on.callback_query(UserCallback.filter_get())
async def user_stats_get(
    message: NonEmptyTextMessage,
    orig_msg: types.Message,
    edit: Callable,
    session: AsyncSession,
    state: FSMContext,
    l10n: TranslatorRunner,
    callback_data: UserCallback | None = None,
):
    if not callback_data:
        user_id = message.text
        if user_id.isdigit():
            user = await User.get_or_none(session, id=int(user_id))
        else:
            user_id = user_id.replace("@", "")
            # ignore case search
            stmt = select(User).filter(func.lower(User.username) == user_id.lower())
            user = (await session.execute(stmt)).scalar()
    else:
        user = await User.get(session, id=callback_data.id)

    if not user:
        return await edit(l10n.get("admin-users-user_not_found"))

    referrals_count = await user.self_referrals_count(session)

    referrer: User = await User.get(session, id=user.referrer_id)
    ref_link = await deep_linking.create_start_link(message.bot, str(user.id))

    answer = ""
    answer += l10n.get("admin-users-tg_premium", premium=user.is_premium) + "\n"
    answer += l10n.get("admin-users-referral_count", referral_count=referrals_count) + "\n"
    answer += (
        l10n.get("admin-users-invited_by", inviter=referrer.pretty() if referrer else "никто")
        + "\n"
    )
    answer += l10n.get("admin-users-ref_link", ref_link=ref_link) + "\n"
    if user.notes:
        answer += l10n.get("admin-users-notes", user_info=user.notes)
    await state.clear()

    return await split_sending_proper(
        orig_msg,
        answer,
        reply_markup=admin_kbs.user_stats(user.id, l10n),
    )


@on.callback_query(UserCallback.filter(F.action == UserAction.REFERRALS))
@flags.session
async def user_referrals(
    call: NonEmptyMessageCallbackQuery,
    edit: Callable,
    callback_data: UserCallback,
    session: AsyncSession,
    state: FSMContext,
    l10n: TranslatorRunner,
):
    await call.answer(l10n.get("admin-users-export_referrals"))
    user = await User.get(session, id=callback_data.id)
    users_with_referrals = await user.get_users_with_referral_counts(
        session, User.referrer_id == user.id
    )
    cache_key = f"referrals_{user.id}"
    excel_file_id = USERS_EXEL_FILE_ID_CACHE.get(cache_key)

    if excel_file_id := USERS_EXEL_FILE_ID_CACHE.get(cache_key):
        document = excel_file_id
    else:
        excel_path = await prepare_users_data_in_chunks(
            users_with_referrals,
            l10n,
            file=f"referrals_{user.id}.csv",
        )
        document = types.FSInputFile(excel_path)

    # Отправляем файл пользователю
    sm = await call.message.answer_document(
        document=document,
        caption=l10n.get("admin-users-export_referrals_done", user=user.pretty()),
    )
    await state.clear()
    USERS_EXEL_FILE_ID_CACHE[cache_key] = sm.document.file_id  # type: ignore


@on.callback_query(UserCallback.filter_delete())
async def delete(
    call: NonEmptyMessageCallbackQuery,
    callback_data: UserCallback,
    state: FSMContext,
    l10n: TranslatorRunner,
):
    assert callback_data.id is not None, "callback_data.id is None"

    data = await state.get_data()
    key = f"{callback_data.__prefix__}_{callback_data.id}"
    if key in data:
        await state.update_data(callback_data=callback_data)
        await call.message.answer(
            l10n.get("admin-users-confirm_delete", code=md.hcode("удалить")),
            reply_markup=helper_kbs.custom_back_kb(cd=UserCallback.new_get(callback_data.id)),
        )
        await state.set_state("delete-confirm")
    else:
        await state.update_data({key: True})
        await call.answer(l10n.get("admin-users-press_again"))


@on.message(StateFilter("delete-confirm"))
async def delete_confirm(
    message: NonEmptyTextMessage,
    edit: Callable,
    state: FSMContext,
    session_manager: PersistenceSessionManager[str],
    l10n: TranslatorRunner,
):
    data = await state.get_data()
    callback_data: UserCallback = data["callback_data"]
    assert callback_data.id is not None, "callback_data.id is None"

    if message.text.lower() != "удалить":
        await state.clear()
        return await edit(
            l10n.get("admin-users-cancelled"),
            reply_markup=helper_kbs.custom_back_kb(cd=UserCallback.new_get(callback_data.id)),
        )

    exists = await LightUser.is_light_exists(session_manager, callback_data.id)
    if not exists:
        await state.clear()
        return await edit(
            l10n.get("admin-users-user_not_found"),
            reply_markup=helper_kbs.custom_back_kb(cd=UserCallback.new_get(callback_data.id)),
        )

    light_user = await LightUser.get_light(session_manager, callback_data.id)
    async with session_manager.db_sessionmaker() as session:
        rich_user = await light_user.get_rich(session)
        await light_user.delete(session)
        await session.commit()

    await message.answer(
        l10n.get("admin-users-user_deleted", user=rich_user.pretty()),
        reply_markup=admin_kbs.back(),
    )
    return await state.clear()


@on.callback_query(UserCallback.filter(F.action == UserAction.ADD_INFO))
async def add_info(
    call: types.CallbackQuery,
    edit: Callable,
    callback_data: UserCallback,
    state: FSMContext,
    l10n: TranslatorRunner,
):
    assert callback_data.id is not None, "callback_data.id is None"

    await state.update_data(callback_data=callback_data)
    await edit(
        l10n.get("admin-users-enter_info"),
        reply_markup=helper_kbs.custom_back_kb(cd=UserCallback.new_get(callback_data.id)),
    )
    await state.set_state("admin:add_info")


@on.message(StateFilter("admin:add_info"))
async def add_info_edit(
    message: types.Message,
    edit: Callable,
    event_from_user: TgUser,
    state: FSMContext,
    session_manager: PersistenceSessionManager[str],
    l10n: TranslatorRunner,
):
    data = await state.get_data()
    note = message.text or message.caption
    if not note:
        return await edit(l10n.get("admin-users-enter_info"))

    callback_data: UserCallback = data["callback_data"]
    assert callback_data.id is not None, "callback_data.id is None"
    lu = await LightUser.get_light(session_manager, callback_data.id)
    async with lu.with_rich() as rich_user:
        username = event_from_user.username or f"ID:{lu.id}"
        rich_user.add_note(username, note)

    await state.clear()

    return await edit(
        l10n.get("admin-users-info_added"),
        reply_markup=helper_kbs.custom_back_kb(
            cd=UserCallback.new_get(callback_data.id),
        ),
    )


@on.callback_query(UserCallback.filter(F.action == UserAction.DELETE_INFO))
async def delete_info(
    call: types.CallbackQuery,
    edit: Callable,
    callback_data: UserCallback,
    state: FSMContext,
    session_manager: PersistenceSessionManager[str],
    l10n: TranslatorRunner,
):
    assert callback_data.id is not None, "callback_data.id is None"

    lu = await LightUser.get_light(session_manager, callback_data.id)
    async with lu.with_rich() as rich_user:
        rich_user.clear_notes()

    await state.clear()

    return await edit(
        l10n.get("admin-users-info_deleted"),
        reply_markup=helper_kbs.custom_back_kb(cd=UserCallback.new_get(callback_data.id)),
    )
