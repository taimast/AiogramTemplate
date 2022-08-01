from aiogram import Router, types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import StatesGroup, State

from project.crying.apps.bot.markups.admin import statistics_markups, admin_markups
from project.crying.db.models import User

router = Router()


class SendMail(StatesGroup):
    preview = State()
    select = State()

    button = State()
    send = State()


async def statistics_start(call: types.CallbackQuery, state: FSMContext):
    await state.clear()

    all_count = await User.count_all()
    today_count = await User.count_new_today()

    # await call.message.answer("Меню статистики", reply_markup=statistics_markups.statistics_start())
    await call.message.answer(
        f"📊 В боте зарегистрировано: {all_count}\n"
        f"📊 Новых пользователей за сегодня: {today_count}\n",
        reply_markup=admin_markups.back()
    )


async def users_count(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    count = await User.count_all()
    await call.message.answer(f"В боте зарегистрировано: {count} 👥",
                              reply_markup=statistics_markups.back())


async def users_count_new(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    count = await User.count_new_today()
    await call.message.answer(f"Новых пользователей за сегодня: {count} 👥",
                              reply_markup=statistics_markups.back())


def register_statistics(dp: Router):
    dp.include_router(router)

    callback = router.callback_query.register
    # message = router.message.register

    callback(statistics_start, text="statistics", state="*")
    callback(users_count, text="users_count", state="*")
    callback(users_count_new, text="users_count_new", state="*")
