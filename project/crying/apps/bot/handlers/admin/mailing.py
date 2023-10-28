import asyncio
from dataclasses import dataclass

from aiogram import Router, types, Bot, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.utils import markdown as md
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from ...keyboards.admin import admin_kbs
from ...keyboards.common import common_kbs
from .....db.models import User

router = Router()


@dataclass
class Mailing:
    success: int = 0
    failed: int = 0
    status_message: types.Message | None = None
    current_emoji: str = "⏳ In progress"
    update_interval: float = 0.6
    send_interval: float = 0.4

    @property
    def status_template(self):
        return f"📨 Total: {md.hcode(self.success + self.failed)}\n" \
               f"✅ Success: {md.hcode(self.success)}\n" \
               f"🚫 Failed: {md.hcode(self.failed)}\n\n" \
               f"{self.current_emoji}\n"

    async def init_status_message(self, message: types.Message):
        self.status_message = await message.answer(
            self.status_template,
            reply_markup=admin_kbs.mailing_cancel()
        )

    async def live_updating_status(self):
        reply_markup = admin_kbs.mailing_cancel()
        while True:
            await asyncio.sleep(self.update_interval)
            self.current_emoji = "⏳ In progress" if self.current_emoji == "⌛ In progress" else "⌛ In progress"
            try:
                await self.status_message.edit_text(
                    self.status_template,
                    reply_markup=reply_markup
                )
            except Exception as e:
                logger.warning(f"Error while updating status message: {e}")

    async def send(self, bot: Bot, user: User, message: types.Message):
        try:
            await bot.copy_message(
                user.id,
                message.chat.id,
                message.message_id,
            )
            self.success += 1
        except Exception as e:
            self.failed += 1
            logger.warning(f"Error while sending message to {user.id}: {e}")

    async def send_to_all(self, bot: Bot, users: list[User], message: types.Message):
        for user in users:
            await self.send(bot, user, message)
            await asyncio.sleep(self.send_interval)

    async def done(self):
        await self.status_message.edit_text(
            self.status_template.replace(self.current_emoji, "✅ Done")
        )

    async def cancel(self):
        await self.status_message.edit_text(
            self.status_template.replace(self.current_emoji, "🚫 Canceled")
        )


@router.callback_query(F.data == "mailing")
async def mailing(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer(
        "Напишите или перешлите сообщение, которое хотите разослать.",
        reply_markup=common_kbs.custom_back("admin")
    )
    await state.set_state("mailing")


@router.message(StateFilter("mailing"))
async def mailing_send(message: types.Message, session: AsyncSession, bot: Bot, state: FSMContext):
    try:
        mailing_obj = Mailing()
        await mailing_obj.init_status_message(message)
        mailing_status_task = asyncio.create_task(mailing_obj.live_updating_status())
        users = await User.all(session)
        mailing_task = asyncio.create_task(mailing_obj.send_to_all(bot, users, message))
        await state.update_data(mailing_task=mailing_task)
        cancelled = False
        try:
            await mailing_task
        except asyncio.CancelledError:
            cancelled = True
        mailing_status_task.cancel()
        try:
            await mailing_status_task
        except asyncio.CancelledError:
            pass

        if cancelled:
            await mailing_obj.cancel()
        else:
            await mailing_obj.done()


    except Exception as e:
        logger.error(f"Error while sending mailing: {e}")
        await message.answer(f"Произошла ошибка при рассылке {e}", parse_mode=None)

    await state.clear()


@router.callback_query(F.data == "mailing_cancel")
async def mailing_cancel(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    mailing_task: asyncio.Task = data.get("mailing_task")
    if mailing_task:
        mailing_task.cancel()
    # # await call.message.edit_reply_markup()
    # await call.message.answer("Рассылка отменена")
    await state.clear()
