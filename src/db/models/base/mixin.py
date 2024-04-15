from typing import Sequence, TypeVar

from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T", bound='Base')


class BaseQuery:

    @classmethod
    async def get_or_create(cls: type[T], session: AsyncSession, defaults=None, **kwargs) -> tuple[T, bool]:
        instance = await cls.get_or_none(session, **kwargs)
        if instance is not None:
            return instance, False
        instance = cls.create(session, **kwargs, **(defaults or {}))
        return instance, True

    @classmethod
    async def get(cls: type[T], session: AsyncSession, **kwargs) -> T:
        if id := kwargs.get('id'):
            return await session.get(cls, id)
        result = await session.execute(select(cls).filter_by(**kwargs))
        return result.unique().scalar_one()

    @classmethod
    async def get_or_none(cls: type[T], session: AsyncSession, **kwargs) -> T | None:
        if id := kwargs.get('id'):
            return await session.get(cls, id)
        result = await session.execute(select(cls).filter_by(**kwargs))
        return result.unique().scalar_one_or_none()

    @classmethod
    def create(cls: type[T], session: AsyncSession, **kwargs) -> T:
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
        res = await session.execute(delete(cls).where(*expr).returning(cls.id))
        return res.unique().scalars().fetchall()

    async def delete_instance(self, session: AsyncSession) -> None:
        await session.delete(self)

    @classmethod
    async def all(cls: type[T], session: AsyncSession) -> list[T]:
        result = await session.execute(select(cls))
        return result.unique().scalars().all()

    def update(self: T, **kwargs) -> None:
        for attr, value in kwargs.items():
            if hasattr(self, attr):
                setattr(self, attr, value)

    @classmethod
    async def filter(
            cls: type[T],
            session: AsyncSession,
            *expr,
            limit: int | None = None,
            offset: int | None = None,
    ) -> list[T]:
        query = select(cls).where(*expr).limit(limit).offset(offset)
        result = await session.execute(query)
        return result.unique().scalars().all()

    @classmethod
    async def count(cls: type[T], session: AsyncSession, *expr) -> int:
        query = select(func.count(cls.id)).where(*expr)
        result = await session.execute(query)
        return result.unique().scalar_one()
