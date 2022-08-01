import logging
import sys
from pathlib import Path

from loguru import logger

from project.crying.config.config import LOG_DIR


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


def init_logging(level="TRACE", steaming=True, write=True):
    logger.remove()
    logging.basicConfig(handlers=[InterceptHandler()], level=0)

    if steaming:
        logger.add(
            sink=sys.stdout,
            level=level,
            enqueue=True,
            diagnose=True,
        )
    if write:
        logger.add(
            sink=Path(LOG_DIR, f"logs.log"),
            level=level,
            enqueue=True,
            encoding="utf-8",
            diagnose=True,
            rotation="00:00",
            compression="zip",
        )


if __name__ == "__main__":
    init_logging(old_logger=True, level="TRACE", old_level=logging.INFO, steaming=True, write=True)
    logger.info("hi")
