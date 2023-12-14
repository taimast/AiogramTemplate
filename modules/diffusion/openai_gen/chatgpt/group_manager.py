import collections
from dataclasses import dataclass, field
from typing import Callable, Awaitable

from .manager import GPTModelManager
from .model import GPTModel, GPTModelName


@dataclass
class GPTGroupManager:
    model_managers: collections.defaultdict[GPTModelName, GPTModelManager] = field(
        default_factory=lambda: collections.defaultdict(GPTModelManager)
    )

    def add_model(self, model: GPTModel):
        self.model_managers[model.model].add_model(model)

    def get_model_manager(self, model_name: GPTModelName) -> GPTModelManager:
        return self.model_managers[model_name]

    def get_model(self, model_name: GPTModelName) -> GPTModel:
        return self.get_model_manager(model_name).models[0]

    def get_model_data(self, model_name: GPTModelName) -> dict:
        return self.get_model(model_name).get_model_data()

    def get_model_names(self) -> list[GPTModelName]:
        return list(self.model_managers.keys())

    async def generate_completion(
            self,
            model_name: GPTModelName,
            messages: list[dict],
            **kwargs,
    ):
        return (
            await self.get_model_manager(model_name)
            .generate_completion(messages, **kwargs)
        )

    async def stream_completion(
            self,
            model_name: GPTModelName,
            messages: list[dict],
            callback: Callable[[str], Awaitable[None]],
            new_chars_threshold: int = 50,
            **kwargs,
    ):
        return (
            await self.get_model_manager(model_name)
            .stream_completion(messages, callback, new_chars_threshold, **kwargs)
        )
