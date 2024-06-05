from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter, CommandObject
from aiogram.fsm.context import FSMContext

from src.config import Settings
from ...callback_data.actions import Action, AdminAction
from ...callback_data.admin import AdminCallback
from ...commands.bot_commands import AdminCommands
from ...keyboards.admin import admin_kbs
from ...keyboards.common import helper_kbs

on = Router(name=__name__)


@on.callback_query(F.data == "admin")
@on.message(Command(AdminCommands.ADMIN))
async def admin_start(message: types.CallbackQuery | types.Message, state: FSMContext):
    await state.clear()
    if isinstance(message, types.CallbackQuery):
        message = message.message
    await message.answer("Админ меню", reply_markup=admin_kbs.admin_start())


@on.callback_query(AdminCallback.filter(F.action == Action.ALL))
async def admins(call: types.CallbackQuery, settings: Settings, state: FSMContext):
    await call.message.answer(
        "Список админов:",
        reply_markup=admin_kbs.admins(settings.bot.admins)
    )


@on.callback_query(AdminCallback.filter(F.action == Action.DELETE))
async def delete_admin(
        call: types.CallbackQuery,
        callback_data: AdminCallback,
        settings: Settings,
        state: FSMContext
):
    data = await state.get_data()
    if callback_data.id == call.from_user.id:
        await call.answer("Нельзя удалить самого себя")
        return
    key = f"admin_{callback_data.id}"
    if key in data:
        settings.bot.admins.remove(callback_data.id)
        await call.message.edit_text(
            f"Админ {callback_data.id} удален",
            reply_markup=admin_kbs.admins(settings.bot.admins)
        )
        settings.dump()
        await state.clear()
    else:
        await state.update_data({key: True})
        await call.answer("Нажмите еще раз для подтверждения")


@on.callback_query(AdminCallback.filter(F.action == Action.CREATE))
async def create_admin(
        call: types.CallbackQuery,
        callback_data: AdminCallback,
        settings: Settings,
        state: FSMContext
):
    await call.message.answer(
        "Введите id админа",
        reply_markup=helper_kbs.custom_back_kb(cd="admin")
    )
    await state.set_state("admin:create")


@on.message(StateFilter("admin:create"))
async def create_admin_id(message: types.Message, settings: Settings, state: FSMContext):
    try:
        admin_id = int(message.text)
    except ValueError:
        await message.answer("Неверный id админа")
        return
    if admin_id in settings.bot.admins:
        await message.answer("Админ уже существует")
        return
    settings.bot.admins.add(admin_id)
    settings.dump()
    await message.answer(
        f"Админ {admin_id} создан",
        reply_markup=admin_kbs.admins(settings.bot.admins)
    )
    await state.clear()


# @on.callback_query(Callback.filter_delete())
# async def delete_vacancy(
#         call: types.CallbackQuery,
#         callback_data: VacancyCallback,
#         settings: Settings,
#         state: FSMContext
# ):
#     data = await state.get_data()
#     key = f"{callback_data.__prefix__}_{callback_data.id}"
#     if key in data:
#         settings.bot.vacancies.pop(callback_data.id)
#         await call.message.edit_text(
#             f"Вакансия {callback_data.id} удалена",
#         )
#         await call.message.answer(
#             "Выберите вакансию:",
#             reply_markup=common_kbs.get_vacancies(settings.bot.vacancies, True)
#         )
#         settings.dump()
#         await state.clear()
#     else:
#         await state.update_data({key: True})
#         await call.answer(f"Нажмите еще раз для подтверждения")

@on.message(Command("sm"))
async def sm(message: types.Message, command: CommandObject, settings: Settings):
    user, text = command.args.split(" ")
    if user.isdigit():
        user = int(user)

    await message.bot.send_message(user, text)
    sm = await message.answer("Отправлено")


@on.callback_query(AdminCallback.filter(F.action == AdminAction.EDIT_TEXTS))
async def edit_texts(call: types.CallbackQuery, settings: Settings, state: FSMContext):
    await call.message.answer(
        "Выберите кнопку для редактирования",
        reply_markup=admin_kbs.edit_texts(settings)
    )


@on.callback_query(AdminCallback.filter(F.action == AdminAction.EDIT_TEXT))
async def edit_text(call: types.CallbackQuery, callback_data: AdminCallback, settings: Settings, state: FSMContext):
    await call.message.answer(
        "Введите новый текст",
        reply_markup=helper_kbs.custom_back_kb(cd="admin")
    )
    await state.set_state("admin:edit_text")
    await state.update_data({"field": callback_data.data})


@on.message(StateFilter("admin:edit_text"))
async def edit_text_message(message: types.Message, settings: Settings, state: FSMContext):
    data = await state.get_data()
    field = data["field"]
    setattr(settings.bot.texts, field, message.text)
    settings.dump()
    await message.answer(
        f"Текст {field} изменен",
        reply_markup=admin_kbs.edit_texts(settings)
    )
    await state.clear()
