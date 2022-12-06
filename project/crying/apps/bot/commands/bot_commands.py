from typing import NamedTuple

from aiogram.types import BotCommand


class _BotCommands(NamedTuple):
    START: BotCommand = BotCommand(command="start", description="Главное меню")

    ADMIN: BotCommand = BotCommand(command="admin", description="Админ меню")

    PROFILE: BotCommand = BotCommand(command="profile", description="Мой профиль")
    ABOUT: BotCommand = BotCommand(command="about", description="О боте")
    HELP: BotCommand = BotCommand(command="help", description="Помощь")
    SUPPORT: BotCommand = BotCommand(command="support", description="Поддержка")
    FEEDBACK: BotCommand = BotCommand(command="feedback", description="Обратная связь")

BotCommands = _BotCommands()

