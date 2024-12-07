from typing import Any, Iterable, Type

from src.db.persistence_session.base import (
    BasePersistenceSession,
    DataInconsistencyError,
    PydanticModelT,
)


class MemoryPersistenceSession(BasePersistenceSession[str]):
    def __init__(self):
        self.data: dict[str, Any] = {}

    async def get(
        self,
        model_class: Type[PydanticModelT],
        key: str,
    ) -> PydanticModelT:
        data = self.data.get(key, None)
        if data is None:
            raise DataInconsistencyError(f"Object with id {key} not found")
        return data

    async def set(
        self,
        model_class: Type[PydanticModelT],
        key: str,
        value: PydanticModelT,
    ):
        self.data[key] = value

    async def exists(
        self,
        model_class: Type[PydanticModelT],
        key: str,
    ) -> bool:
        return key in self.data

    async def all(self, model_class: Type[PydanticModelT], prefix: str) -> list[PydanticModelT]:
        return [self.data[key] for key in self.data if key.startswith(prefix)]

    async def delete(self, model_class: Type[PydanticModelT], key: str):
        del self.data[key]

    async def set_many(
        self,
        model_class: Type[PydanticModelT],
        objects: Iterable[tuple[str, PydanticModelT]],
    ):
        for key, value in objects:
            self.data[key] = value
