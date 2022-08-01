from aiogram import F, Router, types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import StatesGroup, State
from loguru import logger

from project.crying.apps.bot.callback_data.base_callback import ChannelCallback, Action
from project.crying.apps.bot.markups.admin import channel_markups, admin_markups
from project.crying.apps.bot.utils import parse_channel_link, TempData
from project.crying.db.models.base import Channel

router = Router()


class NewChat(StatesGroup):
    done = State()


class NewSponsorChat(StatesGroup):
    done = State()


async def view_chats(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await call.answer()
    chats = await Channel.all()
    await call.message.answer(f"Все чаты для обязательной подписки:",
                              reply_markup=channel_markups.view_channels(chats))


async def create_chat(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer(f"Добавьте бота в чат и сделайте администратором, чтобы проверять подписки.\n"
                              f"Введите ссылку на канал. "
                              f"Введите ссылку по которому должны будут пройти пользователи и через пробел"
                              f" фактическую ссылку на канал для проверки ботом\n"
                              f"Например:\n"
                              f"https://t.me/+bIBc0e-525k2MThi https://t.me/mychannel \nили\n"
                              f"https://t.me/mychannel https://t.me/mychannel",
                              reply_markup=admin_markups.back())
    await state.set_state(NewChat.done)


async def create_chat_done(message: types.Message, state: FSMContext, temp_data: TempData):
    try:
        await state.clear()
        skin, username = parse_channel_link(message.text)
        channel = await Channel.create(skin=skin, username=username)
        temp_data.subscription_channels.append(channel)
        await message.answer(f"Канал для подписки: {channel}\n успешно добавлен", reply_markup=admin_markups.back())
    except Exception as e:
        logger.warning(e)
        await message.answer("Неправильный ввод", reply_markup=admin_markups.back())


async def view_chat(call: types.CallbackQuery, callback_data: ChannelCallback, state: FSMContext):
    await state.clear()
    chat = await Channel.get(pk=callback_data.pk)
    await call.message.answer(f"{chat}",
                              reply_markup=channel_markups.touch_channel(chat))


async def delete_chat(call: types.CallbackQuery,
                      callback_data: ChannelCallback,
                      state: FSMContext,
                      temp_data: TempData):
    await state.clear()
    await state.update_data(delete_chat=callback_data.pk)

    channel = await Channel.get(pk=callback_data.pk)
    await channel.delete()
    temp_data.subscription_channels.remove(channel)

    await call.message.answer(f"Канал для подписки: {channel} успешно удален", reply_markup=admin_markups.back())


def register_channel(dp: Router):
    dp.include_router(router)

    callback = router.callback_query.register
    message = router.message.register

    callback(view_chats, ChannelCallback.filter(F.action == Action.all), state="*")
    callback(create_chat, ChannelCallback.filter(F.action == Action.create), state="*")
    message(create_chat_done, state=NewChat.done)
    callback(view_chat, ChannelCallback.filter(F.action == Action.view), state="*")
    callback(delete_chat, ChannelCallback.filter(F.action == Action.delete), state="*")
