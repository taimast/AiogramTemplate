from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import BotCommandScopeDefault, BotCommandScopeChat
from loguru import logger

from project.crying.apps.bot.commands.bot_commands import BaseCommandsCollection, AdminCommandsCollection, \
    SuperAdminCommandsCollection
from project.crying.config import Settings


async def set_commands(bot: Bot, settings: Settings):
    """ Установка команд бота. """

    async def _set_commands(commands, scope):
        try:
            await bot.set_my_commands(commands, scope=scope)
        except TelegramBadRequest as e:
            logger.warning(f"Can't set commands for {scope}: {e}")

    await _set_commands(BaseCommandsCollection, scope=BotCommandScopeDefault())
    for admin in settings.bot.admins:
        await _set_commands(AdminCommandsCollection, scope=BotCommandScopeChat(chat_id=admin))
    for super_admin in settings.bot.super_admins:
        await _set_commands(SuperAdminCommandsCollection, scope=BotCommandScopeChat(chat_id=super_admin))
