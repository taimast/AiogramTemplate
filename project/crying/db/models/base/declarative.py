from typing import Sequence, TypeVar

from sqlalchemy import select, ChunkedIteratorResult, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

# todo L1 TODO 18.04.2023 17:00 taima: Use func from sqlalchemy_utils. get_tables is not used

T = TypeVar("T", bound='Base')


class Base(DeclarativeBase):
    # type_annotation_map = {
    #     str_30: String(30),
    #     str_50: String(50),
    #     num_12_4: Numeric(12, 4),
    #     num_6_2: Numeric(6, 2),
    # }
    # registry = registry(
    #     type_annotation_map={
    #         # str_30: String(30),
    #         # str_50: String(50),
    #         # num_12_4: Numeric(12, 4),
    #         # num_6_2: Numeric(6, 2),
    #         int: BigInteger,
    #     }
    # )

    @classmethod
    async def get_or_create(cls: type[T], session: AsyncSession, defaults=None, **kwargs) -> tuple[T, bool]:
        instance = await cls.get_or_none(session, **kwargs)
        if instance is not None:
            return instance, False
        instance = await cls.create(session, **kwargs, **(defaults or {}))
        return instance, True

    @classmethod
    async def get(cls: type[T], session: AsyncSession, **kwargs) -> T:
        result = await session.execute(select(cls).filter_by(**kwargs))
        return result.scalar_one()

    @classmethod
    async def get_or_none(cls: type[T], session: AsyncSession, **kwargs) -> T | None:
        result = await session.execute(select(cls).filter_by(**kwargs))
        return result.scalar_one_or_none()

    @classmethod
    async def create(cls: type[T], session: AsyncSession, **kwargs) -> T:
        # ignore extra kwargs
        # todo L1 TODO 17.04.2023 2:59 taima:  use `cls.__table__.columns` instead of `hasattr(cls, k)`
        valid_columns = {c.name for c in cls.__table__.columns}
        kwargs = {k: v for k, v in kwargs.items() if k in valid_columns}
        instance = cls(**kwargs)
        session.add(instance)
        return instance

    # two method to delete instance. One is classmethod, another is instance method

    # удаление по условиям
    @classmethod
    async def delete(cls: type[T], session: AsyncSession, *expr) -> Sequence[int]:
        res: ChunkedIteratorResult = await session.execute(delete(cls).where(*expr).returning(cls.id))
        return res.scalars().fetchall()

    async def delete_instance(self, session: AsyncSession) -> None:
        await session.delete(self)

    @classmethod
    async def all(cls: type[T], session: AsyncSession) -> list[T]:
        result = await session.execute(select(cls))
        return result.scalars().all()

    @classmethod
    async def update(cls: type[T], session: AsyncSession, **kwargs) -> None:
        await session.execute(cls.__table__.update().values(**kwargs))

    @classmethod
    async def filter(
            cls: type[T],
            session: AsyncSession,
            limit: int | None = None,
            offset: int | None = None,
            *expr
    ) -> list[T]:
        query = select(cls).where(*expr).limit(limit).offset(offset)
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def count(cls: type[T], session: AsyncSession, *expr) -> int:
        query = select(func.count(cls.id)).where(*expr)
        result = await session.execute(query)
        return result.scalar_one()
