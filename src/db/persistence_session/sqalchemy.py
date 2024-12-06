from typing import Iterable, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.db.models.base import Base
from src.db.persistence_session.base import BasePersistenceSession, DataInconsistencyError

RichModelT = TypeVar("RichModelT", bound=Base)


class SQLAlchemyPersistenceSession[RichModelT](BasePersistenceSession[int, RichModelT]):
    def __init__(self, session_maker: async_sessionmaker[AsyncSession]):
        self.session_maker = session_maker

    async def get(self, model_class: Type[RichModelT], key: int) -> RichModelT:
        async with self.session_maker() as session:
            obj = await session.get(model_class, id)
            if obj is None:
                raise DataInconsistencyError(f"Object with id {id} not found")
            return obj

    async def set(self, model_class: Type[RichModelT], key: int, value: RichModelT):
        async with self.session_maker() as session:
            session.add(value)
            await session.commit()

    async def exists(self, model_class: Type[RichModelT], key: int) -> bool:
        async with self.session_maker() as session:
            return await session.get(model_class, key) is not None

    async def all(self, model_class: Type[RichModelT], prefix: str) -> list[RichModelT]:
        async with self.session_maker() as session:
            stmt = select(model_class)
            res = await session.execute(stmt)
            return list(res.unique().scalars().all())

    async def delete(self, model_class: Type[RichModelT], key: int):
        async with self.session_maker() as session:
            obj = await session.get(model_class, key)
            if obj is None:
                raise DataInconsistencyError(f"Object with id {key} not found")
            await session.delete(obj)
            await session.commit()

    async def set_many(
        self,
        model_class: Type[RichModelT],
        objects: Iterable[tuple[int, RichModelT]],
    ):
        only_objects = [object for key, object in objects]
        async with self.session_maker() as session:
            session.add_all(only_objects)
            await session.commit()
