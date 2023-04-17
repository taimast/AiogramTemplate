import datetime
from typing import TypeVar

from sqlalchemy import String, BigInteger, select
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, DeclarativeBase
from sqlalchemy.orm import mapped_column

T = TypeVar("T", bound=DeclarativeBase)


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
    async def get_or_create1(cls: type[T], session: AsyncSession, defaults=None, **kwargs) -> tuple[T, bool]:
        filters = {k: v for k, v in kwargs.items() if not k.startswith('_')}
        instance = (await session.execute(select(cls).filter_by(**filters))).one()
        if instance is None:
            params = {k: v for k, v in kwargs.items() if not k.startswith('_')}
            if defaults:
                params.update(defaults)
            instance = cls(**params)
            session.add(instance)
            await session.commit()
            return instance, True
        return instance, False

    @classmethod
    async def get_or_create(cls: type[T], session: AsyncSession, defaults=None, **kwargs) -> tuple[T, bool]:
        instance = await cls.get_or_none(session, **kwargs)
        if instance is not None:
            return instance, False
        instance = await cls.create(session, **kwargs, **(defaults or {}))
        return instance, True

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
        await session.commit()
        return instance


class AbstractUser(Base):
    __abstract__ = True
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str | None] = mapped_column(String(32), index=True)
    first_name: Mapped[str | None] = mapped_column(String(100))
    last_name: Mapped[str | None] = mapped_column(String(100))
    is_bot: Mapped[bool] = mapped_column(default=False)
    is_premium: Mapped[bool | None]

    @classmethod
    async def get_or_create(cls, session: AsyncSession, **kwargs):
        pass


class TimestampMixin:
    created_at: Mapped[datetime.datetime | None] = mapped_column(
        server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )
