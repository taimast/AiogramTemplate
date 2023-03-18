import argparse
from enum import Enum
from pprint import pformat
from typing import Type

from loguru import logger
from pydantic import BaseModel

from project.crying.config.config import Settings
from project.crying.config.logg_settings import LogSettings, Level


class Mode(str, Enum):
    PROD = "prod"
    DEV = "dev"
    TEST = "test"


class CLIArgsSettings(BaseModel):
    mode: Mode = Mode.PROD
    log: LogSettings = LogSettings()
    webhook: bool = False
    config_file: str | None
    env_file: str | None

    @classmethod
    def parse_args(cls) -> 'CLIArgsSettings':
        parser = argparse.ArgumentParser()
        parser.add_argument("-m", "--mode", type=str, default="prod", help="prod or dev")
        parser.add_argument("-w", "--webhook", action="store_true", help="Use webhook", default=False)
        parser.add_argument("-f", "--config-file", type=str, help="yaml config file")

        args = parser.parse_args()
        args_dict = args.__dict__.copy()
        logger.info(f"args_dict:\n{pformat(args_dict)}")
        args_settings = cls(**args_dict)

        if args_settings.mode is Mode.PROD:
            args_settings.log.stdout = None
            args_settings.log.file = Level.INFO
            args_settings.config_file = args_settings.config_file or "config.yaml"
            args_settings.env_file = args_settings.env_file or r"..\..\.env"
        else:
            args_settings.config_file = args_settings.config_file or "config_dev.yaml"
            args_settings.env_file = args_settings.env_file or r"..\..\.env_dev"

        logger.info(f"CLI args:\n{pformat(args_settings.dict())}")
        return args_settings

    def update_settings(self, settings_cls: Type[Settings]):
        settings_cls.__config__.config_file = self.config_file
        settings_cls.__config__.env_file = self.env_file
