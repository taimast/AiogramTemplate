from typing import Iterable, Type

from redis.asyncio import Redis

from src.db.persistence_session.base import BasePersistenceSession, DataInconsistencyError
from src.db.persistence_session.memory import PydanticModelT


class RedisPersistenceSession(BasePersistenceSession[str, PydanticModelT]):
    def __init__(self, redis: Redis):
        self.redis = redis.json()

    async def get(self, model_class: Type[PydanticModelT], key: str) -> PydanticModelT:
        data = await self.redis.get(key)  # type: ignore
        if data is None:
            raise DataInconsistencyError(f"Object with id {id} not found")
        return model_class.model_validate(data)

    async def set(self, model_class: Type[PydanticModelT], key: str, value: PydanticModelT):
        await self.redis.set(
            key,
            ".",
            value.model_dump(mode="json"),
        )  # type: ignore

    async def exists(self, model_class: Type[PydanticModelT], key: str) -> bool:
        return await self.redis.client.exists(key)

    async def all(self, model_class: Type[PydanticModelT], prefix: str) -> list[PydanticModelT]:
        keys = await self.redis.client.keys(f"{prefix}*")
        objs = await self.redis.mget(  # type: ignore
            keys,
            ".",
        )
        return [model_class.model_validate(obj) for obj in objs]

    async def delete(self, model_class: Type[PydanticModelT], key: str):
        await self.redis.delete(key)  # type: ignore

    async def set_many(
        self,
        model_class: Type[PydanticModelT],
        objects: Iterable[tuple[str, PydanticModelT]],
    ):
        objs = [(key, ".", value.model_dump(mode="json")) for key, value in objects]
        await self.redis.mset(objs)  # type: ignore
