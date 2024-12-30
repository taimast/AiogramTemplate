from __future__ import annotations

from pprint import pformat

from aiogram import Bot, F, Router, types
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from fluentogram import TranslatorRunner
from loguru import logger

from src.apps.bot.commands.bot_commands import BaseCommands
from src.apps.bot.keyboards.common import common_kbs
from src.apps.bot.types.message import NonEmptyBotMessage
from src.apps.bot.types.user import TgUser
from src.utils.support import SupportConnector

on = Router(name=__name__)


@on.message(CommandStart(deep_link=True))
async def deep_start(
    msg: types.Message,
    bot: Bot,
    command: CommandObject,
    l10n: TranslatorRunner,
    state: FSMContext,
):
    """Deep link start handler"""
    logger.info(
        f"Deep link start: {pformat(msg.model_dump(exclude_none=True, exclude_unset=True))}"
    )
    # if command.args:
    #     referrer_id = int(command.args)
    #     # if user.set_referrer(referrer_id):
    #     #     await session.commit()

    # await start(msg, l10n, state)


@on.message(Command(BaseCommands.START))
@on.message(F.text.startswith("«"))
@on.callback_query(F.data == "start")
async def start(
    msg: types.Message | types.CallbackQuery,
    l10n: TranslatorRunner,
    state: FSMContext,
    event_from_user: TgUser,
):
    logger.info(
        f"Start: {pformat(msg.model_dump(exclude_none=True, exclude_unset=True))}"
    )

    await state.clear()
    if isinstance(msg, types.CallbackQuery):
        assert isinstance(msg.message, types.Message), "msg.message is not a Message"
        msg = msg.message

    assert msg.from_user, "msg.from_user is None"

    total_text = ""
    total_text += l10n.get("emails", unreadEmails=0) + "\n"
    total_text += l10n.get("emails", unreadEmails=1) + "\n"
    total_text += l10n.get("emails", unreadEmails=42) + "\n"
    total_text += l10n.get("emails", unreadEmails=43) + "\n"
    total_text += l10n.get("dpi-ratio", ratio=43) + "\n"
    # total_text += l10n.get("pref-page.title") + "\n"
    sm = await msg.answer(
        total_text,
        # event_from_user.mention_html(),
        # reply_markup=common_kbs.languages(l10n),
        reply_markup=common_kbs.inline_start(),
    )


@on.message(Command(BaseCommands.HELP))
async def help(
    msg: types.Message,
    l10n: TranslatorRunner,
    state: FSMContext,
    support_connector: SupportConnector | None,
):
    if not support_connector:
        return await msg.answer(
            "В данный момент невозможно подключиться к службе поддержки"
        )
    if not msg.from_user:
        return await msg.answer("Не удалось получить информацию о пользователе")

    await support_connector.create_thread(msg.from_user)

    return await msg.answer(
        "Вы создали новую тему в чате поддержки, введите ваш вопрос",
    )


@on.message(Command("refund"))
async def refund(msg: NonEmptyBotMessage):
    transactions = await msg.bot.get_star_transactions()

    for transaction in transactions.transactions:
        print(pformat(transaction.model_dump(exclude_none=True, exclude_unset=True)))
        # await msg.bot.refund_star_payment(transaction.source.user.id, transaction.id)


@on.message(Command("get_mention"))
async def get_mention(message: types.Message):
    await message.answer(f"Your mention: {message.from_user.mention_html()}")
    await message.answer(
        f"Your mention: {message.from_user.mention_html()}", parse_mode=None
    )
    other_guy_link = "tg://user?id=7161347153"
    hlink_text = f'<a href="{other_guy_link}">Other guy</a>'
    await message.answer(f"Other guy: {hlink_text}")
