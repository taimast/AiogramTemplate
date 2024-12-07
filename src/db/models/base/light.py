from __future__ import annotations

import abc
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, ClassVar, Self, Type, TypeVar

from pydantic import BaseModel, ConfigDict, PrivateAttr
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.db.models.base import Base as BaseRich
from src.db.persistence_session.base import DataInconsistencyError
from src.db.persistence_session.manager import PersistenceSessionManager

RichModelT = TypeVar("RichModelT", bound=BaseRich)


class LightBase[RichModelT](BaseModel, abc.ABC):
    model_config = ConfigDict(
        frozen=True,
        arbitrary_types_allowed=True,
    )
    _session_manager: PersistenceSessionManager[str] | None = PrivateAttr()

    id: int

    if TYPE_CHECKING:
        __key__: ClassVar[str]
        __rich_model__: ClassVar[Type[RichModelT]]  # type: ignore
    else:

        @property
        @abc.abstractmethod
        def __key__(self) -> str:
            pass

        @property
        @abc.abstractmethod
        def __rich_model__(self) -> Type[RichModelT]:
            pass

    # def model_post_init(self, __context: Any) -> None:
    #     if __context:
    #         self.session_manager = __context["session_manager"]
    #     raise ValueError("model_post_init should not be called")

    @property
    def key(self) -> str:
        return f"{self.__key__}:{self.id}"

    @classmethod
    def make_key(cls, id: int) -> str:
        return f"{cls.__key__}:{id}"

    @classmethod
    async def is_light_exists(
        cls,
        session_manager: PersistenceSessionManager[str],
        id: int,
    ) -> bool:
        key = cls.make_key(id)
        return await session_manager.light.exists(cls, key)

    @classmethod
    async def get_light(
        cls,
        session_manager: PersistenceSessionManager[str],
        id: int,
    ) -> Self:
        key = cls.make_key(id)
        obj = await session_manager.light.get(cls, key)
        obj.as_(session_manager)
        return obj

    @classmethod
    async def create_light[T: LightBase](
        cls: Type[T],
        session_manager: PersistenceSessionManager[str],
        model: T,
    ) -> T:
        # TODO: add custom encoding
        await session_manager.light.set(
            cls,
            model.key,
            model,
        )
        return model

    @classmethod
    async def create_rich(
        cls,
        model: RichModelT,
        session_manager: PersistenceSessionManager[str] | None = None,
        session: AsyncSession | None = None,
    ) -> RichModelT:
        if not session_manager and session:
            session.add(model)
            return model
        if session_manager:
            async with session_manager.db_sessionmaker() as session:
                session.add(model)
                await session.commit()
                return model
        else:
            raise ValueError("session_manager or session should be set")

    @classmethod
    async def get_rich_by_id(
        cls,
        session_manager: PersistenceSessionManager[str],
        id: int,
    ) -> RichModelT | None:
        async with session_manager.db_sessionmaker() as session:
            return await session.get(cls.__rich_model__, id)

    @property
    def session_manager(self) -> PersistenceSessionManager[str]:
        if not self._session_manager:
            raise ValueError("session_manager is not set")
        return self._session_manager

    def as_(self, session_manager: PersistenceSessionManager[str]):
        self._session_manager = session_manager
        return self

    async def _get_rich(self, session: AsyncSession) -> RichModelT:
        rich = await session.get(self.__rich_model__, self.id)
        if not rich:
            raise DataInconsistencyError(f"Rich model with id {self.id} not found")
        return rich

    async def get_rich(self, session: AsyncSession | None = None) -> RichModelT:
        if not session:
            async with self.session_manager.db_sessionmaker() as session:
                return await self._get_rich(session)
        else:
            return await self._get_rich(session)

    @asynccontextmanager
    async def with_rich(self):
        async with self.session_manager.db_sessionmaker() as session:
            rich = await session.get(self.__rich_model__, self.id)
            if not rich:
                raise DataInconsistencyError(f"Rich model with id {self.id} not found")
            yield rich
            await session.commit()

    async def _delete_rich_with_session(self, session: AsyncSession):
        rich = await session.get(self.__rich_model__, self.id)
        if not rich:
            raise DataInconsistencyError(f"Rich model with id {self.id} not found")
        await session.delete(rich)

    async def _delete_rich(self, session: AsyncSession | None = None):
        if not session:
            async with self.session_manager.db_sessionmaker() as session:
                await self._delete_rich_with_session(session)
                await session.commit()

        else:
            await self._delete_rich_with_session(session)

    async def delete(self, session: AsyncSession | None = None):
        await self.session_manager.light.delete(self.__class__, self.key)
        await self._delete_rich(session)
