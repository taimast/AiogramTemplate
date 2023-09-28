from __future__ import annotations

import abc
from abc import ABC
from typing import Generic, TypeVar

T = TypeVar('T', bound='Observer')


class Observer(ABC):
    @abc.abstractmethod
    async def trigger(self, *args, **kwargs):
        raise NotImplementedError

    async def __call__(self, *args, **kwargs):
        return await self.trigger(*args, **kwargs)


class Observable(Generic[T]):
    def __init__(self):
        self.observers: list[T] = []

    def register(self, observer: T) -> None:
        if observer not in self.observers:
            self.observers.append(observer)

    def unregister(self, observer: T) -> None:
        if observer in self.observers:
            self.observers.remove(observer)

    async def trigger(self, *args, **kwargs) -> None:
        for observer in self.observers:
            await observer.trigger(*args, **kwargs)
