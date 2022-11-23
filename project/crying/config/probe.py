from enum import Enum

from loguru import logger
from pydantic import BaseModel

from project.crying.config.logg_settings import init_logging


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


class Some(BaseModel):
    level: Level
    stream: bool = True
    write: bool = True
    base_logger: bool = True
# long name for function
def long_name_for_function():
    logger.warning("Hello, world!")

def some_long_name():
    logger.critical("Hello, world! Critical")


def main():
    s = Some(level=Level.INFO, stream=True, write=True, base_logger=True)
    init_logging(s.level)
    logger.info("Hello, world!")
    long_name_for_function()
    some_long_name()

if __name__ == '__main__':
    main()
