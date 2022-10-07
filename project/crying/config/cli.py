import argparse
from enum import Enum
from pprint import pformat

from loguru import logger
from pydantic import BaseModel


class Mode(str, Enum):
    PROD = "prod"
    DEV = "dev"
    TEST = "test"


class LogSettings(BaseModel):
    level: str = "INFO"
    stream: bool = True
    write: bool = True
    base_logger: bool = True


class CLIArgsSettings(BaseModel):
    mode: Mode = Mode.PROD
    log: LogSettings = LogSettings()

    @classmethod
    def add_log_group(cls, parser):
        log_subparser = parser.add_argument_group("log", "Log settings")
        log_subparser.add_argument("-ll", "--log-level", type=str, default="INFO", help="Log level")
        log_subparser.add_argument("-ls", "--log-stream", action="store_true", help="Log to stream")
        log_subparser.add_argument("-lw", "--log-write", action="store_true", help="Log to file")
        log_subparser.add_argument("-lb", "--log-base-logger", action="store_true", help="Log to base logger")
        return log_subparser

    @classmethod
    def add_log_subparser(cls, parser: argparse.ArgumentParser):
        log_subparser = parser.add_subparsers(title="log", description="Log settings", dest="log")
        new_parser = log_subparser.add_parser("log", help="Log settings")
        new_parser.add_argument("-ll", "--log-level", type=str, default="INFO", help="Log level")
        new_parser.add_argument("-ls", "--log-stream", action="store_true", help="Log to stream")
        return log_subparser

    @classmethod
    def get_cli_args(cls) -> 'CLIArgsSettings':
        parser = argparse.ArgumentParser()
        parser.add_argument("-m", "--mode", type=str, default="prod", help="prod or dev")
        args = parser.parse_args()
        args_dict = args.__dict__.copy()
        args_settings = cls(**args_dict)
        if args_settings.mode is Mode.PROD:
            args_settings.log.stream = False
        logger.info(f"CLI args:\n{pformat(args_settings.dict())}")
        return args_settings

    @property
    def is_prod(self) -> bool:
        return self.mode is Mode.PROD


cli_settings = CLIArgsSettings.get_cli_args()
