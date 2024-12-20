from aiogram import Bot
from aiogram.types import CallbackQuery, Message


class NonEmptyBotMessage(Message):
    bot: Bot  # type: ignore


class NonEmptyTextMessage(NonEmptyBotMessage):
    text: str  # type: ignore


class NonEmptyMessageCallbackQuery(CallbackQuery):
    data: str  # type: ignore
    bot: Bot  # type: ignore
    message: Message  # type: ignore
