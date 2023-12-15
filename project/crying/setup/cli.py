import argparse
from enum import Enum
from pprint import pformat
from typing import Type

from loguru import logger
from pydantic import BaseModel

from .log import LogSettings, Level
from ..config import Settings


class Mode(str, Enum):
    PROD = "prod"
    DEV = "dev"
    TEST = "test"


# todo L1 TODO 16.04.2023 21:43 taima: Переделать парсер командной строки
class CLIArgsSettings(BaseModel):
    mode: Mode = Mode.PROD
    log: LogSettings = LogSettings()
    webhook: bool = False
    config_file: str | None
    env_file: str | None = None

    def update_settings(self, settings_cls: Type[Settings]):
        settings_cls.model_config["config_file"] = self.config_file
        settings_cls.model_config["env_file"] = self.env_file


def parse_args() -> CLIArgsSettings:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-m", "--mode",
        type=str,
        default="dev",
        help="prod or dev"
    )
    parser.add_argument(
        "-w", "--webhook",
        action="store_true",
        help="Use webhook",
        default=False
    )
    parser.add_argument(
        "-f", "--config-file",
        type=str,
        help="yaml config file"
    )

    args = parser.parse_args()
    args_dict = args.__dict__.copy()
    logger.info(f"args_dict:\n{pformat(args_dict)}")
    args_settings = CLIArgsSettings(**args_dict)

    if args_settings.mode is Mode.DEV:
        args_settings.log.stdout = Level.DEBUG
        args_settings.config_file = args_settings.config_file or "config_dev.yml"
        args_settings.env_file = args_settings.env_file or r"..\..\.env_dev"
    else:
        args_settings.log.stdout = None
        args_settings.log.file = Level.INFO
        args_settings.config_file = args_settings.config_file or "config.yml"
        args_settings.env_file = args_settings.env_file or r"..\..\.env"

    logger.info(f"CLI args:\n{pformat(args_settings.dict())}")
    return args_settings
