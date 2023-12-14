from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from io import BytesIO
from typing import BinaryIO, Literal

import openai
import pydub
from openai import AsyncClient

from ..diffusion import DiffusionModel, DiffusionType


@dataclass
class OpenAIDiffusionModel(DiffusionModel):
    client: AsyncClient |None = None

    async def predict(self, prompt: str) -> str:
        raise NotImplementedError


class DallEVersion(StrEnum):
    V2 = "dall-e-2"
    V3 = "dall-e-3"


@dataclass
class DallE(OpenAIDiffusionModel):
    model: DallEVersion = DallEVersion.V3
    type = DiffusionType.TEXT_TO_IMAGE

    async def predict(self, prompt: str) -> str:
        response = await self.client.images.generate(
            model=self.model,
            prompt=prompt,
        )
        return response.data[0].url


@dataclass
class Whisper(OpenAIDiffusionModel):
    model: Literal["whisper-1"] = "whisper-1"
    type = DiffusionType.AUDIO_TO_TEXT

    async def predict(self, voice_prompt: BinaryIO) -> str:
        speech = pydub.AudioSegment.from_file(voice_prompt)
        out_io = BytesIO()
        out_io.name = "audio.wav"
        speech.export(out_io, format="wav")
        response = await self.client.audio.transcriptions.create(
            model=self.model,
            file=out_io,
        )
        return response.text


@dataclass
class DAVinci(OpenAIDiffusionModel):
    model: Literal["text-davinci-003"] = "text-davinci-003"
    type = DiffusionType.TEXT_TO_TEXT

    async def predict(self, prompt: str, extra_inputs: dict | None = None) -> str:
        inputs = self.default_inputs
        if extra_inputs:
            for key, value in extra_inputs.items():
                if key in inputs:
                    inputs[key] = value
        response = await openai.Completion.create(
            model=self.model,
            prompt=prompt,
            **inputs,
        )
        return response["choices"][0]["text"]
