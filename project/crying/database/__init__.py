import asyncio

from loguru import logger
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import close_all_sessions

from project.crying.config import SqliteDB, PostgresDB
from project.crying.database.models.base import Base
from project.crying.database.models.user import User

Database = SqliteDB | PostgresDB


async def close_db():
    close_all_sessions()
    logger.info(f"Database closed")


async def init_db(db: Database = SqliteDB()) -> async_sessionmaker:
    logger.debug(f"Initializing Database {db.database}[{db.host}]...")
    engine = create_async_engine(db.url, echo=True)
    logger.debug(f"Database {db.database}[{db.host}] initialized")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    logger.debug(f"Database {db.database}[{db.host}] tables created")
    return async_sessionmaker(engine, expire_on_commit=False)


async def main():
    maker = await init_db(PostgresDB(database="probe_alchemy"))
    async with maker() as session:
        async with session.begin():
            session.add(User())
            await session.commit()


if __name__ == '__main__':
    asyncio.run(main())
