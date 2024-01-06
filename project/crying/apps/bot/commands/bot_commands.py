import functools
from typing import NamedTuple

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import BotCommand


def command_wrapper(on: Router, command: BotCommand):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # kwargs.update({"command_info": command.command})
            result = await func(*args, **kwargs)
            return result

        on.message.register(wrapper, Command(command))
        on.message.register(wrapper, F.text.startswith(command.description[0]))
        on.callback_query.register(wrapper, F.data == command.command)
        return func

    return decorator


class _BaseCommands(NamedTuple):
    START: BotCommand = BotCommand(command="start", description="🏠 Главное меню")


class _AdminCommands(NamedTuple):
    ADMIN: BotCommand = BotCommand(command="admin", description="👮‍♂️ Админка")


class _SuperAdminCommands(NamedTuple):
    SUPER_ADMIN: BotCommand = BotCommand(command="super_admin", description="👮‍♂️ Супер админка")


BaseCommands = _BaseCommands()
AdminCommands = _AdminCommands()
SuperAdminCommands = _SuperAdminCommands()

BaseCommandsCollection = BaseCommands
AdminCommandsCollection = AdminCommands + BaseCommandsCollection
SuperAdminCommandsCollection = SuperAdminCommands + AdminCommandsCollection
