import asyncio

from aiogram import Router, types, Bot, F
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
        reply_markup=helper_kbs.custom_back_kb("admin")
    )

    await state.set_state("start_mailing")


@on.message(StateFilter("start_mailing"))
async def add_buttons(message: types.Message, state: FSMContext):
    await state.update_data(send_message=message)
    await message.answer(
        "Добавьте кнопки для сообщения в формате кнопка1-ссылка1. Каждый с новой строки. Или нажмите Пропустить",
        reply_markup=admin_kbs.add_buttons()
    )
    await state.set_state("pre-mailing")


@on.message(StateFilter("pre-mailing"))
@on.callback_query(F.data == "send_mailing")
async def mailing_send(message: types.Message, session: AsyncSession, bot: Bot, state: FSMContext):
    data = await state.get_data()
    send_message: types.Message = data.get("send_message")
    if isinstance(message, types.CallbackQuery):
        send_reply_markup = send_message.reply_markup
        message = message.message
    else:
        send_reply_markup = admin_kbs.created_buttons(message.text)

    await state.update_data(
        send_reply_markup=send_reply_markup,
        send_message=send_message
    )

    await message.bot.copy_message(
        chat_id=message.chat.id,
        from_chat_id=message.chat.id,
        message_id=send_message.message_id,
        reply_markup=send_reply_markup
    )

    await message.answer(
        "Отправить рассылку?",
        reply_markup=admin_kbs.confirm_mailing()
    )


@on.callback_query(F.data == "confirm_mailing")
async def mailing_send(call: types.CallbackQuery, session: AsyncSession, bot: Bot,
                       state: FSMContext):
    data = await state.get_data()
    send_message: types.Message = data.get("send_message")
    send_reply_markup = data.get("send_reply_markup")
    message = call.message

    try:
        data = await state.get_data()
        interval = data.get("interval", 0.4)
        mailing_obj = Mailing(
            update_interval=60,
            send_interval=interval,
            cancel_markup=admin_kbs.mailing_cancel()
        )
        await mailing_obj.init_status_message(message)
        mailing_status_task = asyncio.create_task(mailing_obj.live_updating_status())
        users = await User.all(session)
        user_ids = [user.id for user in users]
        mailing_task = asyncio.create_task(
            mailing_obj.send_notifications(bot, user_ids, send_message, send_reply_markup))
        await state.update_data(
            mailing_task=mailing_task,
            mailing_obj=mailing_obj
        )
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
        await message.answer("☑️ Рассылка завершена", reply_markup=admin_kbs.back())

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
        await call.message.edit_text("Рассылка отозвана", reply_markup=admin_kbs.admin_start())
    else:
        await call.message.answer("Нет последних рассылок")


@on.callback_query(AdminCallback.filter_mailing_cancel())
async def mailing_cancel(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    mailing_task: asyncio.Task = data.get("mailing_task")
    confirm_cancel: bool = data.get("confirm_cancel", False)

    if not confirm_cancel:
        await call.answer("Вы уверены, что хотите отменить рассылку?")
        await state.update_data(confirm_cancel=True)
        return

    if mailing_task:
        mailing_task.cancel()
        await call.message.answer("Рассылка отменяется ...")
    else:
        await call.answer("Нет активных рассылок")
    # # await call.message.edit_reply_markup()
    await state.clear()


@on.callback_query(F.data == "update_mailing_stats")
async def mailing_cancel(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    mailing_obj: Mailing = data.get("mailing_obj")
    if mailing_obj:
        await mailing_obj.update_status()
    else:
        await call.answer("Нет активных рассылок")
