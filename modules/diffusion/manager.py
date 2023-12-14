from functools import cache
from typing import Any

from diffusion_bot.apps.diffusion.diffusion import DiffusionModel, DiffusionType
from diffusion_bot.apps.diffusion.math_api.mathpix import MathPix
from diffusion_bot.apps.diffusion.midjourney.midjourney import MidjourneyWorker
from diffusion_bot.apps.diffusion.midjourney.model import MidjourneyDiffusionModel
from diffusion_bot.apps.diffusion.openai_gen.chatgpt.group_manager import GPTGroupManager
from diffusion_bot.apps.diffusion.openai_gen.chatgpt.model import GPTModel
from diffusion_bot.apps.diffusion.openai_gen.models import Whisper, DallE, OpenAIDiffusionModel
from diffusion_bot.apps.diffusion.replicate_gen.base import Replicate
from diffusion_bot.apps.diffusion.replicate_gen.models import ReplicateDiffusionModel


class DiffusionManager:
    def __init__(
            self,
            gpt_group_manager: GPTGroupManager,
            replicate: Replicate,
            midjourney_worker: MidjourneyWorker,
            mathpix: MathPix,

            openai_models: list[GPTModel, DallE, Whisper],
            replicate_models: list[ReplicateDiffusionModel],
            photo_scaler_models: list[ReplicateDiffusionModel],
            midjourney_models: list[MidjourneyDiffusionModel],
    ):
        self.replicate = replicate
        self.midjourney_worker = midjourney_worker
        self.gpt_group_manager = gpt_group_manager
        self.mathpix = mathpix

        self.openai_models = openai_models
        self.replicate_models = replicate_models
        self.photo_scaler_models = photo_scaler_models
        self.midjourney_models = midjourney_models

        self.models = (
                self.midjourney_models
                + self.openai_models
                + self.replicate_models
                + self.photo_scaler_models
        )

    @cache
    def get_model(self, model_name: str) -> DiffusionModel:
        for model in self.models:
            if model.name == model_name:
                return model

    @cache
    def get_models(self, type: DiffusionType = None) -> list[DiffusionModel]:
        # todo L1 TODO 11.06.2023 19:31 taima: Возможно затратная операция, добавить кеширование
        if type is None:
            return self.models

        models = []
        for model in self.models:
            if model.type == type:
                models.append(model)
        return models

    async def predict(self, model_name: str, prompt: Any = None, **kwargs) -> Any:
        model = self.get_model(model_name)
        if isinstance(model, ReplicateDiffusionModel):
            return await self.replicate.predict(model, prompt)

        elif isinstance(model, GPTModel):
            return await self.gpt_group_manager.stream_completion(model.model, **kwargs)
        else:
            model: OpenAIDiffusionModel
            return await model.predict(prompt)
