import asyncio

from aiogram import Router, types, Bot, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.utils import markdown as md
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from ...keyboards.common import common_kbs
from .....db.models import User

router = Router()


@router.callback_query(F.data == "mailing")
async def mailing(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer(
        "Напишите или перешлите сообщение, которое хотите разослать.",
        reply_markup=common_kbs.custom_back("admin")
    )
    await state.set_state("mailing")


@router.message(StateFilter("mailing"))
async def mailing_send(message: types.Message, session: AsyncSession, bot: Bot, state: FSMContext):
    time_emoji1 = "⏳ In progress"
    time_emoji2 = "⌛ In progress"
    done_emoji = "✅ Done"
    current_emoji = time_emoji1

    status_template = (
        "📨 Total: {}\n"
        "✅ Success: {}\n"
        "🚫 Failed: {}\n\n"
        "{}\n"
    )
    try:
        status_message = await message.answer(status_template.format(0, 0, 0, current_emoji))
        success = 0
        failed = 0

        async def mailings_status_updated():
            while True:
                await asyncio.sleep(0.5)
                nonlocal current_emoji
                current_emoji = time_emoji1 if current_emoji == time_emoji2 else time_emoji2
                try:
                    await status_message.edit_text(
                        status_template.format(
                            md.hcode(success + failed),
                            md.hcode(success),
                            md.hcode(failed),
                            current_emoji
                        )
                    )
                except Exception as e:
                    logger.warning(f"Error while updating status message: {e}")

        task = asyncio.create_task(mailings_status_updated())
        # copy message
        users = await User.all(session)
        for num, user in enumerate(users, 1):
            try:
                await bot.copy_message(
                    user.id,
                    message.chat.id,
                    message.message_id,
                )
                success += 1
            except Exception as e:
                failed += 1
                logger.warning(f"Error while sending message to {user.id}: {e}")
            await asyncio.sleep(0.1)
        task.cancel()
        await status_message.edit_text(
            status_template.format(
                md.hcode(success + failed),
                md.hcode(success),
                md.hcode(failed),
                done_emoji,
            )
        )
    except Exception as e:
        logger.error(f"Error while sending mailing: {e}")
        await message.answer(f"Произошла ошибка при рассылке {e}", parse_mode=None)

    await state.clear()
