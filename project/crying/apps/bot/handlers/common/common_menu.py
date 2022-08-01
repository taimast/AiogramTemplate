from aiogram import Router, types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.utils import markdown as md

from project.crying.apps.bot.markups.common import common_markups
from project.crying.apps.bot.middleware.language import _
from project.crying.apps.bot.utils import is_subscribed_to_channel, TempData
from project.crying.config.config import Bot
from project.crying.db.models import User

router = Router()


async def start(message: types.Message | types.CallbackQuery, user: User, state: FSMContext):
    await state.clear()
    if isinstance(message, types.CallbackQuery):
        message = message.message
    await message.answer("Стартовое меню!")


async def check_subscribe(call: types.CallbackQuery, state: FSMContext, bot: Bot, temp_data:TempData):
    await state.clear()
    if await is_subscribed_to_channel(call.from_user.id, bot, temp_data.subscription_channels):
        await call.message.answer(_("✅ Подписки найдены, введите {} чтобы продолжить").format(md.hpre("start")),
                                  reply_markup=common_markups.check_subscribe())
        return True
    await call.answer(_("❌ Ты подписался не на все каналы"), show_alert=True)
    return False


def register_common(dp: Router):
    dp.include_router(router)

    callback = router.callback_query.register
    message = router.message.register

    message(start, commands="start", state="*")
    callback(start, text="start", state="*")
    callback(check_subscribe, text="check_subscribe", state="*")
