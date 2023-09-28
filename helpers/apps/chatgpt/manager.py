import asyncio
import dataclasses
from contextlib import asynccontextmanager
from typing import List, Callable, Awaitable, AsyncGenerator

from loguru import logger

from .model import GPTModel


@dataclasses.dataclass
class GPTModelManager:
    """ Manages multiple GPTModel instances and rate limits them """
    models: List[GPTModel] = dataclasses.field(default_factory=list)
    requests_per_minute: int = 200  # todo L1 TODO 08.09.2023 20:52 taima:  Увеличить до 60

    _available_models: asyncio.Queue[GPTModel] = dataclasses.field(init=False)
    _rate_limit_semaphores: dict[GPTModel, asyncio.BoundedSemaphore] = dataclasses.field(init=False)

    def __post_init__(self):
        self._available_models = asyncio.Queue()
        self._rate_limit_semaphores = {}
        for model in self.models:
            self.add_model(model)

    def add_model(self, model: GPTModel):
        self.models.append(model)
        self._rate_limit_semaphores[model] = asyncio.BoundedSemaphore(self.requests_per_minute)
        self._available_models.put_nowait(model)

    @asynccontextmanager
    async def acquire_model(self) -> AsyncGenerator[GPTModel, None]:
        # model = await self._available_models.get()
        # fixme L1 08.08.2023 21:05 taima: Доработать логику для работы с несколькими аккаунтами GPT
        model = self.models[0]
        semaphore = self._rate_limit_semaphores[model]
        await semaphore.acquire()

        try:
            yield model
        finally:
            # self._available_models.put_nowait(model)
            asyncio.get_event_loop().call_later(60, semaphore.release)

    async def generate_completion(self, messages: List[dict], **kwargs):
        async with self.acquire_model() as model:
            return await model.generate_completion(messages, **kwargs)

    async def stream_completion(
            self,
            messages: List[dict],
            callback: Callable[[str], Awaitable[None]],
            new_chars_threshold: int = 50,
            **kwargs,
    ):
        async with self.acquire_model() as model:
            logger.info(f"Using model {model.model}")
            return await model.stream_completion(messages, callback, new_chars_threshold, **kwargs)
