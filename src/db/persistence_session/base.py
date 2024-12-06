import abc
from typing import Iterable, Type


class DataInconsistencyError(Exception):
    """Exception raised when there is a data inconsistency between Redis and the database."""

    def __init__(self, message: str):
        super().__init__(message)


class BasePersistenceSession[K, V](abc.ABC):
    @abc.abstractmethod
    async def get(self, model_class: Type[V], key: K) -> V:
        """Интерфейс для получения объекта по ID
        Если объект не существует, то выбрасывает DataInconsistencyError
        """

    @abc.abstractmethod
    async def set(self, model_class: Type[V], key: K, value: V):
        """Интерфейс для сохранения объекта"""

    @abc.abstractmethod
    async def exists(self, model_class: Type[V], key: K) -> bool:
        """Интерфейс для проверки существования ключа"""

    @abc.abstractmethod
    async def all(self, model_class: Type[V], prefix: str) -> list[V]:
        """Интерфейс для получения всех объектов"""

    @abc.abstractmethod
    async def delete(self, model_class: Type[V], key: K):
        """Интерфейс для удаления объекта по ID"""

    @abc.abstractmethod
    async def set_many(self, model_class: Type[V], objects: Iterable[tuple[K, V]]):
        """Интерфейс для установки нескольких объектов"""
