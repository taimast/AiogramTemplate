import logging
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from loguru import logger
from pydantic import BaseModel

from ..config import LOG_DIR


class Level(str, Enum):
    # 5
    TRACE = "TRACE"
    # 10
    DEBUG = "DEBUG"
    # 20
    INFO = "INFO"
    # 25
    SUCCESS = "SUCCESS"
    # 30
    WARNING = "WARNING"
    # 40
    ERROR = "ERROR"
    # 50
    CRITICAL = "CRITICAL"


class LogSettings(BaseModel):
    stdout: Level | None = Level.INFO
    file: Level | None = None
    file_name: str = "src.log"
    redirect_base_logger: bool = True


@dataclass
class Format:
    minimal: str = "<u><m>{time:HH:mm:ss}</m></u> <lvl>{level:<8}</lvl> <r>|</r> <lvl>{message}</lvl>"
    middle: str = ("<m>{time:HH:mm:ss}</m> <lvl>{level:<8}</lvl> "
                   "<fg 136,136,198>[{line:>4}]</fg 136,136,198> <r>|</r> "
                   "<fg 255,198,109>{module}</fg 255,198,109> - "
                   "<lvl>{message}</lvl>")
    default: str = ("<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                    "<level>{level: <8}</level> | "
                    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                    "<level>{message}</level>")

    # default: str = None


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def init_logging(log_settings: LogSettings):
    # Intercept standard logging

    if log_settings.redirect_base_logger:
        logging.basicConfig(handlers=[InterceptHandler()], level=0)

    handlers = []
    if log_settings.stdout is not None:
        handlers.append(dict(
            sink=sys.stderr,
            level=log_settings.stdout,
            # format=Format.middle,
            # enqueue=True,
            backtrace=True,
            diagnose=True,
        ))
    if log_settings.file is not None:
        handlers.append(dict(
            sink=Path(LOG_DIR) / log_settings.file_name,
            level=log_settings.file,
            # enqueue=True,
            backtrace=True,
            diagnose=True,

            encoding="utf-8",
            rotation="00:00",
            compression="zip",
        ))

    logger.configure(
        handlers=handlers,
        # activation=[('tortoise', False)]
    )
