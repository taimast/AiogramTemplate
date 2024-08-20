from dataclasses import dataclass

from aiogram import Bot
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.config import Settings


@dataclass(frozen=True)
class SetupOpts:
    session_maker: async_sessionmaker
    bot: Bot
    settings: Settings
    l10n: TranslatorRunner
