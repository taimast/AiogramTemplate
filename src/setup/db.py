from loguru import logger
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlalchemy.orm import close_all_sessions

from src.db.models import Base

from ..config import PostgresDB, SqliteDB

Database = SqliteDB | PostgresDB


async def close_db():
    close_all_sessions()
    logger.info("Database closed")


async def init_db(db: Database = PostgresDB.default(), echo: bool = False) -> async_sessionmaker:
    logger.info(f"Initializing {db}...")
    engine = create_async_engine(db.url, echo=echo)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info(f"Database {db} initialized")
    return async_sessionmaker(engine, expire_on_commit=False)
