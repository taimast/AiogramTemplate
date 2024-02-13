import asyncio

from aiogram import Router, types, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from ...callback_data.admin import AdminCallback
from ...keyboards.admin import admin_kbs
from ...keyboards.common import helper_kbs
from .....db.models import User
from .....utils.mailing import Mailing

on = Router(name=__name__)


@on.callback_query(AdminCallback.filter_mailing())
async def mailing(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer(
        "Напишите или перешлите сообщение, которое хотите разослать.",
        reply_markup=helper_kbs.custom_back("admin")
    )
    await state.set_state("mailing")


@on.message(StateFilter("mailing"))
async def mailing_send(message: types.Message, session: AsyncSession, bot: Bot, state: FSMContext):
    try:
        mailing_obj = Mailing(
            cancel_markup=admin_kbs.mailing_cancel()
        )
        await mailing_obj.init_status_message(message)
        mailing_status_task = asyncio.create_task(mailing_obj.live_updating_status())
        users = await User.all(session)
        user_ids = [user.id for user in users]
        mailing_task = asyncio.create_task(mailing_obj.send_to_all(bot, user_ids, message))
        await state.update_data(mailing_task=mailing_task)
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
        await message.answer("Админ меню", reply_markup=admin_kbs.admin_start())

    except Exception as e:
        logger.error(f"Error while sending mailing: {e}")
        await message.answer(f"Произошла ошибка при рассылке {e}", parse_mode=None)

    await state.clear()


@on.callback_query(AdminCallback.filter_retract_last_mailing())
async def retract_last_mailing(call: types.CallbackQuery, bot: Bot):
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
        await call.message.edit_text("Рассылка отозвана")
    else:
        await call.message.answer("Нет последних рассылок")


@on.callback_query(AdminCallback.filter_mailing_cancel())
async def mailing_cancel(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    mailing_task: asyncio.Task = data.get("mailing_task")
    if mailing_task:
        mailing_task.cancel()
    # # await call.message.edit_reply_markup()
    # await call.message.answer("Рассылка отменена")
    await state.clear()
