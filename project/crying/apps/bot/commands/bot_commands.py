from typing import NamedTuple

from aiogram.types import BotCommand


class _BaseCommands(NamedTuple):
    START: BotCommand = BotCommand(command="start", description="Главное меню")
    PROFILE: BotCommand = BotCommand(command="profile", description="Мой профиль")
    ABOUT: BotCommand = BotCommand(command="about", description="О боте")
    HELP: BotCommand = BotCommand(command="help", description="Помощь")
    SUPPORT: BotCommand = BotCommand(command="support", description="Поддержка")
    FEEDBACK: BotCommand = BotCommand(command="feedback", description="Обратная связь")


class _AdminCommands(NamedTuple):
    ADMIN: BotCommand = BotCommand(command="admin", description="Админ меню")


class _SuperAdminCommands(NamedTuple):
    SUPER_ADMIN: BotCommand = BotCommand(command="super_admin", description="Супер админ меню")


BaseCommands = _BaseCommands()
AdminCommands = _AdminCommands() + BaseCommands
SuperAdminCommands = _SuperAdminCommands() + AdminCommands
