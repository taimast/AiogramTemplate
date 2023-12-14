import typing
from dataclasses import dataclass, field
from enum import StrEnum
from openai import AsyncClient

class DiffusionType(StrEnum):
    TEXT_TO_IMAGE = "text2image"
    TEXT_TO_TEXT = "text2text"
    TEXT_TO_VIDEO = "text2video"
    TEXT_TO_AUDIO = "text2audio"
    AUDIO_TO_TEXT = "audio2text"
    IMAGE_TO_IMAGE = "image2image"
    IMAGE_TO_TEXT = "image2text"

    def get_text(self, l10n) -> str:
        return l10n.get(f"diffusion-type-button-{self}")

    @classmethod
    def to_text_types(cls) -> list['DiffusionType']:
        return [cls.TEXT_TO_TEXT, cls.AUDIO_TO_TEXT, cls.IMAGE_TO_TEXT]

    @classmethod
    def to_image_types(cls) -> list['DiffusionType']:
        return [cls.TEXT_TO_IMAGE, cls.IMAGE_TO_IMAGE]


@dataclass
class DiffusionModel:
    model: str
    name: str | None = None
    type: DiffusionType = DiffusionType.TEXT_TO_IMAGE
    default_inputs: dict[str, typing.Any] = field(default_factory=dict)
