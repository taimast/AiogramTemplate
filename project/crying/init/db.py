import asyncio

from loguru import logger
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import close_all_sessions

from project.crying.database.models.invoice import AbstractInvoice
from ..config import SqliteDB, PostgresDB
from ..database.models.base import Base
from ..database.models.user import User

Database = SqliteDB | PostgresDB


async def close_db():
    close_all_sessions()
    logger.info(f"Database closed")


async def init_db(db: Database = PostgresDB.default()) -> async_sessionmaker:
    logger.debug(f"Initializing Database {db.database}[{db.host}]...")
    engine = create_async_engine(db.url, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    logger.debug(f"Database {db.database}[{db.host}] initialized")
    return async_sessionmaker(engine, expire_on_commit=False)


async def main():
    maker = await init_db(PostgresDB(database="probe_alchemy"))
    async with maker() as session:
        async with session.begin():
            # session.add(User())
            user, _ = await User.get_or_create(session, id=1)
            invoice, _ = await AbstractInvoice.get_or_create(session, id="2", user_id=user.id)
            logger.info(invoice.user.id)
            # await session.commit()


if __name__ == '__main__':
    asyncio.run(main())
