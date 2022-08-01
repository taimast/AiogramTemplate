import asyncpg
from loguru import logger
from tortoise import Tortoise

__all__ = (
    "init_db",
    "models",
    "utils"
)

from project.crying.config import Database, config, MODELS_DIR


async def init_db(db: Database = config.db):
    logger.debug(f"Initializing Database {db.database}[{db.host}]...")
    data = {
        "db_url": db.url,
        "modules": {"models": [MODELS_DIR]},
    }
    try:
        await Tortoise.init(**data)
        await Tortoise.generate_schemas()
    except asyncpg.exceptions.ConnectionDoesNotExistError as e:
        logger.warning(e)
        logger.info("Creating a new database ...")
        await Tortoise.init(**data, _create_db=True)
        await Tortoise.generate_schemas()
        logger.success(f"New database {db.database} created")

    logger.debug(f"Database {db.database}[{db.host}] initialized")
