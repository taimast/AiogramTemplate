from aiogram import Router, types
from aiogram.filters import StateFilter, Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardRemove

from support_bot.apps.bot.keyboards.admin import admin_kbs
from support_bot.config import Settings
from support_bot.db.models import User

router = Router(name=__name__)


class ExportUsers(StatesGroup):
    choice_send_type = State()
    finish = State()


@router.callback_query(Text("add_admins"))
async def add_admins(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Введи id админов через пробел", reply_markup=ReplyKeyboardRemove())
    await state.set_state("add_admins")


@router.message(StateFilter("add_admins"))
async def add_admins_handler(message: types.Message, user: User, settings: Settings, state: FSMContext):
    admins = message.text.split()
    for admin in admins:
        if admin.isdigit():
            admin = int(admin)
            settings.bot.admins.append(admin)
            settings.dump()

    await message.answer(f"Добавлены админы {admins}", reply_markup=admin_kbs.admin_start())
    await state.clear()


@router.callback_query(Text("delete_admins"))
async def delete_admins(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Введи id админов через пробел", reply_markup=ReplyKeyboardRemove())
    await state.set_state("delete_admins")


@router.message(StateFilter("delete_admins"))
async def delete_admins_handler(message: types.Message, user: User, settings: Settings, state: FSMContext):
    admins = message.text.split()
    for admin in admins:
        if admin.isdigit():
            admin = int(admin)
            settings.bot.admins.remove(admin)
            settings.dump()

    await message.answer(f"Удалены админы {admins}", reply_markup=admin_kbs.admin_start())
    await state.clear()


@router.callback_query(Text("admins"))
async def adminds(call: types.CallbackQuery, settings: Settings, user: User):
    await call.message.answer(f"Админы: {settings.bot.admins}",
                              reply_markup=admin_kbs.admin_start())
