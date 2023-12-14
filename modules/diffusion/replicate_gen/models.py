import re
import typing
from dataclasses import dataclass, field

from diffusion_bot.apps.diffusion.diffusion import DiffusionType, DiffusionModel

MODEL_RE = re.compile(r"^(?P<model>[^/]+/[^:]+):(?P<version>.+)$")

Url: typing.TypeAlias = str


@dataclass
class ReplicateDiffusionModel(DiffusionModel):
    version: str = field(init=False)
    cost: float = 0.00055
    prompt_field: str = "prompt"

    def __post_init__(self):
        self.version = MODEL_RE.match(self.model).group("version")

    def parse_output(self, prediction: dict) -> Url:
        if self.type == DiffusionType.TEXT_TO_IMAGE:
            return prediction["output"][0]
        elif self.type == DiffusionType.TEXT_TO_VIDEO:
            return prediction["output"]["mp4"]
        elif self.type == DiffusionType.TEXT_TO_AUDIO:
            output = prediction["output"]
            if isinstance(output, str):
                return output
            return output.get("audio_out") or output.get("audio")
        elif self.type == DiffusionType.AUDIO_TO_TEXT:
            text = ""
            for item in prediction["output"]:
                text += item["text"]
            return text
        else:
            # todo L1 TODO 16.06.2023 14:42 taima: У некоторых моделей несколько вариантов результатов, возможно стоит добавить обработку всех
            output = prediction["output"]
            if isinstance(output, list):
                output = output[-1]
                if isinstance(output, dict):
                    return iter(output.values()).__next__()
                return output
            elif isinstance(output, dict):
                return iter(output.values()).__next__()
            return prediction["output"]
