from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import BotCommandScopeChat, BotCommandScopeAllPrivateChats
from loguru import logger

from ..apps.bot.commands.bot_commands import BaseCommandsCollection, AdminCommandsCollection, \
    SuperAdminCommandsCollection
from ..config import Settings


async def set_commands(bot: Bot, settings: Settings):
    """
    Set bot commands
    :param bot:
    :param settings:
    :return:
    """

    async def _set_commands(commands, scope):
        try:
            await bot.set_my_commands(commands, scope=scope)
        except TelegramBadRequest as e:
            logger.warning(f"Can't set commands for {scope}: {e}")

    # await _set_commands(BaseCommandsCollection, scope=BotCommandScopeDefault())
    await _set_commands(BaseCommandsCollection, scope=BotCommandScopeAllPrivateChats())
    for admin in settings.bot.admins:
        await _set_commands(AdminCommandsCollection, scope=BotCommandScopeChat(chat_id=admin))
    for super_admin in settings.bot.super_admins:
        await _set_commands(SuperAdminCommandsCollection, scope=BotCommandScopeChat(chat_id=super_admin))
    logger.info("Bot commands set")
