from typing import NamedTuple

from aiogram.types import BotCommand


class _BaseCommands(NamedTuple):
    START: BotCommand = BotCommand(command="start", description="🏠 Главное меню")
    PROFILE: BotCommand = BotCommand(command="profile", description="👤 Мой профиль")
    ABOUT: BotCommand = BotCommand(command="about", description="ℹ️ О боте")
    SUPPORT: BotCommand = BotCommand(command="support", description="👨‍💻 Поддержка")
    FEEDBACK: BotCommand = BotCommand(command="feedback", description="🗣️ Обратная связь")


class _AdminCommands(NamedTuple):
    ADMIN: BotCommand = BotCommand(command="admin", description="👮‍♂️ Админка")
    BASE_ADMIN: BotCommand = BotCommand(command="base_admin", description="👮‍♂️ Базовое админ меню")


class _SuperAdminCommands(NamedTuple):
    SUPER_ADMIN: BotCommand = BotCommand(command="super_admin", description="👮‍♂️ Супер админка")


BaseCommands = _BaseCommands()
AdminCommands = _AdminCommands()
SuperAdminCommands = _SuperAdminCommands()

BaseCommandsCollection = BaseCommands
AdminCommandsCollection = AdminCommands + BaseCommandsCollection
SuperAdminCommandsCollection = SuperAdminCommands + AdminCommandsCollection
