import asyncio

from loguru import logger
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import close_all_sessions
from sqlalchemy_utils import database_exists, create_database

from project.crying.db.models import Base, User
from ..config import SqliteDB, PostgresDB

Database = SqliteDB | PostgresDB


async def close_db():
    close_all_sessions()
    logger.info(f"Database closed")


async def dev_init_db(db: Database = PostgresDB.default()) -> async_sessionmaker:
    logger.info(f"Initializing Database {db.database}[{db.host}]...")
    engine = create_async_engine(db.url, echo=True)

    if not database_exists(db.sync_url):
        create_database(db.sync_url)
        logger.info(f"Database {db.database}[{db.host}] created")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    logger.info(f"Database {db.database}[{db.host}] initialized")
    return async_sessionmaker(engine, expire_on_commit=False)


async def init_db(db: Database = PostgresDB.default(), dev: bool = False) -> async_sessionmaker:
    if dev:
        return await dev_init_db(db)
    logger.info(f"Initializing {db}...")
    engine = create_async_engine(db.url)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info(f"Database {db} initialized")
    return async_sessionmaker(engine, expire_on_commit=False)


async def get_user(maker, user_id):
    async with maker() as session:
        user, _ = await User.get_or_create(session, id=user_id)
        return user


async def main():
    maker = await init_db(PostgresDB(database="probe_alchemy3"))

    async with maker() as session:
        # session.add(User())
        user, _ = await User.get_or_create(session, id=1)
        await session.commit()
        async with user:
            await session.commit()
            logger.info(f"User locked {user.id} {user.locked}")
            user = await get_user(maker, user.id)
            logger.info(f"Gotten user {user.id} {user.locked}")
            await asyncio.sleep(5)

        logger.info("User unlocked")

        # await user.delete_instance(session)
        # await session.flush()
        # await asyncio.sleep(4)
        # user.first_name = "Vasya"
        # await session.commit()
        # print(await User.update(session, language_code=Locale.ENGLISH))

        # users = await User.all(session)
        # print(type(users))
        # print(users)
        # for u in users:
        #     print(u.language_code)
        # invoice, _ = await AbstractInvoice.get_or_create(session, id="2", user_id=user.id)
        # await asyncio.sleep(5)
        # res = await User.delete(session, User.id == 1)
        # print(res)
        # logger.info(invoice.user.id)
        # await session.commit()


if __name__ == '__main__':
    asyncio.run(main())
