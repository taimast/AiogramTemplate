from aiogram import Bot
from aiogram.types import BusinessConnection, CallbackQuery, InlineQuery, Message


class FilledMessage(Message):
    text: str  # type: ignore
    bot: Bot  # type: ignore
    business_connection_id: str  # type: ignore


class FilledCallbackQuery(CallbackQuery):
    data: str  # type: ignore
    bot: Bot  # type: ignore
    message: Message  # type: ignore


class FilledBusinessConnection(BusinessConnection):
    bot: Bot  # type: ignore


class FilledInlineQuery(InlineQuery):
    bot: Bot  # type: ignore


class NonEmptyBotMessage(Message):
    bot: Bot  # type: ignore


class NonEmptyTextMessage(NonEmptyBotMessage):
    text: str  # type: ignore


class NonEmptyMessageCallbackQuery(CallbackQuery):
    data: str  # type: ignore
    bot: Bot  # type: ignore
    message: Message  # type: ignore
