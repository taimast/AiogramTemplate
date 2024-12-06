from aiogram import F, Router, flags
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.bot.types.message import NonEmptyMessageCallbackQuery, NonEmptyTextMessage
from src.config import Settings
from src.config.moderator import Moderator
from src.db.models import User
from src.db.models.user.light import LightUser
from src.db.persistence_session.manager import PersistenceSessionManager

from ...callback_data.actions import ModeratorAction
from ...callback_data.moderator import ModeratorCallback
from ...keyboards.admin import admin_kbs
from ...keyboards.common import helper_kbs

on = Router(name=__name__)


@on.callback_query(ModeratorCallback.filter_all())
async def moderators(call: NonEmptyMessageCallbackQuery, settings: Settings, l10n):
    await call.message.answer(
        "Список модераторов:",
        reply_markup=admin_kbs.get_moderators(settings.bot.moderators, l10n),
    )


@on.callback_query(ModeratorCallback.filter_create())
async def create_moderator(call: NonEmptyMessageCallbackQuery, state: FSMContext):
    await call.message.answer(
        "Введите id или username пользователя, которого хотите сделать модератором",
        reply_markup=helper_kbs.custom_back_kb(cd="admin"),
    )

    await state.set_state("create_moderator")


@on.message(StateFilter("create_moderator"))
@flags.session
async def create_moderator_msg(
    msg: NonEmptyTextMessage,
    settings: Settings,
    session: AsyncSession,
    state: FSMContext,
    l10n,
):
    if msg.text.isdigit():
        mod_user = await User.get_or_none(session, id=int(msg.text))
    else:
        mod_user = await User.get_or_none(session, username=msg.text)

    if not mod_user:
        return await msg.answer(
            "Пользователь не найден", reply_markup=helper_kbs.custom_back_kb(cd="admin")
        )

    moderator = Moderator(id=mod_user.id, username=mod_user.username)
    settings.bot.moderators[mod_user.id] = moderator
    settings.dump()
    await msg.answer(
        f"Модератор @{mod_user.pretty()} добавлен",
        reply_markup=admin_kbs.get_moderator(moderator, l10n),
    )

    return await state.clear()


@on.callback_query(ModeratorCallback.filter_get())
async def get_moderator(
    call: NonEmptyMessageCallbackQuery,
    callback_data: ModeratorCallback,
    settings: Settings,
    session_manager: PersistenceSessionManager[str, LightUser],
    l10n,
):
    assert callback_data.id is not None, "callback_data.id is None"
    mod_exists = await LightUser.is_light_exists(session_manager, callback_data.id)
    if not mod_exists:
        return await call.answer("Пользователь не найден")

    mod_user = await LightUser.get_light(session_manager, callback_data.id)
    rich_user = await mod_user.get_rich()

    moder = settings.bot.moderators[callback_data.id]

    return await call.message.answer(
        f"Модератор: {rich_user.pretty()}",
        reply_markup=admin_kbs.get_moderator(moder, l10n),
    )


@on.callback_query(ModeratorCallback.filter(F.action == ModeratorAction.SWITCH))
async def switch_moderator(
    call: NonEmptyMessageCallbackQuery,
    callback_data: ModeratorCallback,
    settings: Settings,
    state: FSMContext,
    l10n,
):
    assert callback_data.id is not None, "callback_data.id is None"
    assert callback_data.permission is not None, "callback_data.permission is None"

    moder = settings.bot.moderators[callback_data.id]
    moder.switch_permission(callback_data.permission)
    settings.dump()
    await call.message.edit_reply_markup(
        reply_markup=admin_kbs.get_moderator(moder, l10n),
    )


@on.callback_query(ModeratorCallback.filter_delete())
async def delete_moderator(
    call: NonEmptyMessageCallbackQuery,
    callback_data: ModeratorCallback,
    settings: Settings,
    state: FSMContext,
    l10n,
):
    assert callback_data.id is not None, "callback_data.id is None"
    data = await state.get_data()
    key = f"{callback_data.__prefix__}_{callback_data.id}"
    if key in data:
        del settings.bot.moderators[callback_data.id]
        settings.dump()
        await call.message.edit_text(
            f"Модератор {callback_data.id} удален",
            reply_markup=admin_kbs.get_moderators(settings.bot.moderators, l10n),
        )
        await state.clear()
    else:
        await state.update_data({key: True})
        await call.answer("Нажмите еще раз для подтверждения")
