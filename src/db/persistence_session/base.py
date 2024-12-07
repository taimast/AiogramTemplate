import abc
from typing import Iterable, Type, TypeVar

from pydantic import BaseModel

PydanticModelT = TypeVar("PydanticModelT", bound=BaseModel)


class DataInconsistencyError(Exception):
    """Exception raised when there is a data inconsistency between Redis and the database."""

    def __init__(self, message: str):
        super().__init__(message)


class BasePersistenceSession[K](abc.ABC):
    @abc.abstractmethod
    async def get(self, model_class: Type[PydanticModelT], key: K) -> PydanticModelT:
        """Интерфейс для получения объекта по ID
        Если объект не существует, то выбрасывает DataInconsistencyError
        """

    @abc.abstractmethod
    async def set(self, model_class: Type[PydanticModelT], key: K, value: PydanticModelT):
        """Интерфейс для сохранения объекта"""

    @abc.abstractmethod
    async def exists(self, model_class: Type[PydanticModelT], key: K) -> bool:
        """Интерфейс для проверки существования ключа"""

    @abc.abstractmethod
    async def all(self, model_class: Type[PydanticModelT], prefix: str) -> list[PydanticModelT]:
        """Интерфейс для получения всех объектов"""

    @abc.abstractmethod
    async def delete(self, model_class: Type[PydanticModelT], key: K):
        """Интерфейс для удаления объекта по ID"""

    @abc.abstractmethod
    async def set_many(
        self,
        model_class: Type[PydanticModelT],
        objects: Iterable[tuple[K, PydanticModelT]],
    ):
        """Интерфейс для установки нескольких объектов"""
