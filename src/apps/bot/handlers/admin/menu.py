from typing import Callable

from aiogram import F, Router, types
from aiogram.filters import Command, CommandObject, StateFilter
from aiogram.fsm.context import FSMContext
from fluentogram import TranslatorRunner

from src.apps.bot.types.message import NonEmptyBotMessage, NonEmptyTextMessage
from src.config import Settings
from src.db.models.user.light import LightUser

from ...callback_data.actions import Action, AdminAction
from ...callback_data.admin import AdminCallback
from ...commands.bot_commands import AdminCommands
from ...keyboards.admin import admin_kbs
from ...keyboards.common import helper_kbs

on = Router(name=__name__)


@on.callback_query(F.data == "admin")
@on.message(Command(AdminCommands.ADMIN))
async def admin_start(
    message: types.CallbackQuery | types.Message,
    edit: Callable,
    light_user: LightUser,
    settings: Settings,
    state: FSMContext,
    l10n: TranslatorRunner,
):
    await state.clear()
    await edit(
        l10n.get("admin-menu"),
        reply_markup=admin_kbs.admin_start(light_user.id, settings.bot, l10n),
    )


@on.callback_query(AdminCallback.filter(F.action == Action.ALL))
async def admins(
    call: types.CallbackQuery,
    edit: Callable,
    settings: Settings,
    state: FSMContext,
    l10n: TranslatorRunner,
):
    await edit(
        l10n.get("admin-list"),
        reply_markup=admin_kbs.admins(settings.bot.admins, l10n),
    )


@on.callback_query(AdminCallback.filter(F.action == Action.DELETE))
async def delete_admin(
    call: types.CallbackQuery,
    edit: Callable,
    callback_data: AdminCallback,
    settings: Settings,
    state: FSMContext,
    l10n: TranslatorRunner,
):
    assert callback_data.id is not None, "callback_data.id is None"

    data = await state.get_data()
    if callback_data.id == call.from_user.id:
        await call.answer(l10n.get("admin-delete-self_error"))
        return
    key = f"admin_{callback_data.id}"
    if key in data:
        settings.bot.admins.remove(callback_data.id)
        await edit(
            l10n.get("admin-delete-success", admin_id=callback_data.id),
            reply_markup=admin_kbs.admins(settings.bot.admins, l10n),
        )
        settings.dump()
        await state.clear()
    else:
        await state.update_data({key: True})
        await call.answer(l10n.get("admin-delete-confirm"))


@on.callback_query(AdminCallback.filter(F.action == Action.CREATE))
async def create_admin(
    call: types.CallbackQuery,
    edit: Callable,
    callback_data: AdminCallback,
    settings: Settings,
    state: FSMContext,
    l10n,
):
    await edit(
        l10n.get("admin-create-prompt"),
        reply_markup=helper_kbs.custom_back_kb(cd="admin"),
    )
    await state.set_state("admin:create")


@on.message(StateFilter("admin:create"))
async def create_admin_id(
    message: NonEmptyTextMessage,
    settings: Settings,
    state: FSMContext,
    l10n: TranslatorRunner,
):
    try:
        admin_id = int(message.text)
    except ValueError:
        return await message.answer(l10n.get("admin-create-invalid_id"))
    if admin_id in settings.bot.admins:
        return await message.answer(l10n.get("admin-create-exists"))

    settings.bot.admins.add(admin_id)
    settings.dump()

    await message.answer(
        l10n.get("admin-create-success", admin_id=admin_id),
        reply_markup=admin_kbs.admins(settings.bot.admins, l10n),
    )
    return await state.clear()


@on.message(Command("sm"))
async def sm(
    message: NonEmptyBotMessage,
    command: CommandObject,
    settings: Settings,
):
    if not command.args:
        return await message.answer("Не указан пользователь или текст")

    user, text = command.args.split(" ")
    if user.isdigit():
        user = int(user)

    await message.bot.send_message(user, text)

    return await message.answer("Отправлено")


@on.callback_query(AdminCallback.filter(F.action == AdminAction.EDIT_TEXTS))
async def edit_texts(
    call: types.CallbackQuery,
    edit: Callable,
    settings: Settings,
    state: FSMContext,
):
    await edit(
        "Выберите кнопку для редактирования",
        reply_markup=admin_kbs.edit_texts(settings),
    )


@on.callback_query(AdminCallback.filter(F.action == AdminAction.EDIT_TEXT))
async def edit_text(
    call: types.CallbackQuery,
    edit: Callable,
    callback_data: AdminCallback,
    settings: Settings,
    state: FSMContext,
):
    await edit(
        "Введите новый текст",
        reply_markup=helper_kbs.custom_back_kb(cd="admin"),
    )
    await state.set_state("admin:edit_text")
    await state.update_data({"field": callback_data.data})


@on.message(StateFilter("admin:edit_text"))
async def edit_text_message(
    message: types.Message,
    settings: Settings,
    state: FSMContext,
):
    data = await state.get_data()
    field = data["field"]
    setattr(settings.bot.texts, field, message.text)
    settings.dump()
    await message.answer(f"Текст {field} изменен", reply_markup=admin_kbs.edit_texts(settings))
    await state.clear()
