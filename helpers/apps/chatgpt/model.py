import typing
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Callable, Awaitable

import openai


class DiffusionType(StrEnum):
    TEXT_TO_TEXT = "text2text"


class GPTModelName(StrEnum):
    # gpt-3.5-turbo
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    # gpt-4
    GPT_4 = "gpt-4"


@dataclass
class GPTModel:
    model: GPTModelName
    name: str
    max_tokens: int
    api_key: str | None = None
    type: DiffusionType = DiffusionType.TEXT_TO_TEXT
    default_inputs: dict[str, typing.Any] = field(default_factory=dict)

    def __hash__(self):
        return hash(id(self))

    def get_model_data(self):
        return {
            "model": self.model,
            "api_key": self.api_key,
        }

    async def _request(self, messages: list[dict], stream: bool = False, **kwargs):
        return await openai.ChatCompletion.acreate(
            **self.get_model_data(),
            messages=messages,
            stream=stream,
            **kwargs,
        )

    async def generate_completion(
            self,
            messages: list[dict],
            **kwargs,
    ):
        response = await self._request(messages, **kwargs)
        return response.choices[0].message.content

    async def stream_completion(
            self,
            messages: list[dict],
            callback: Callable[[str], Awaitable[None]],
            new_chars_threshold: int = 50,
            **kwargs,
    ):
        text = ""
        new_chars = 0
        response = await self._request(messages, stream=True, **kwargs)
        async for message in response:
            delta = message.choices[0].delta
            if "content" in delta:
                text += delta["content"]
                new_chars += len(delta["content"])

            if new_chars >= new_chars_threshold:
                await callback(text + "\n...")
                # todo L1 TODO 30.04.2023 2:54 taima:
                new_chars = 0

        await callback(text)
        return text
