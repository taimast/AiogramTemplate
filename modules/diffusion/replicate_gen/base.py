import asyncio
import re
import typing
from dataclasses import dataclass
from pprint import pformat

import aiohttp
from loguru import logger
from replicate.files import upload_file
from replicate.json import encode_json

from diffusion_bot.apps.diffusion.diffusion import DiffusionType
from diffusion_bot.apps.diffusion.replicate_gen.models import ReplicateDiffusionModel

Url: typing.TypeAlias = str


# data can be: {'input': {'image': 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAVABUAAD/4gHbSUNDX1BST0ZJTEUAAQEAAAHLAAAAAAJAAABtbnRyUkdCIFhZWiAAAAAAAAAAAAAAAABhY3NwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAA9tYAAQAAAADTLVF0BQ8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAlyWFlaAAAA8AAAABRnWFlaAAABBAAAABRiWFlaAAABGAAAABR3dHB0AAABLAAAABRjcHJ0AAABQAAAAAxyVFJDAAABTAAAACBnVFJDAAABTAAAACBiVFJDAAABTAAAACBkZXNjAAABbAAAAF9YWVogAAAAAAAAb58AADj0AAADkVhZWiAAAAAAAABilgAAt4cAABjcWFlaIAAAAAAAACShAAAPhQAAttNYWVogAAAAAAAA808AAQAAAAEWwnRleHQAAAAATi9BAHBhcmEAAAAAAAMAAAACZmYAAPKnAAANWQAAE9AAAApbZGVzYwAAAAAAAAAFc1JHQgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD/2wBDAAQDAwQDAwQEAwQFBAQFBgoHBgYGBg0JCggKDw0QEA8NDw4RExgUERIXEg4PFRwVFxkZGxsbEBQdHx0aHxgaGxr...
# need dont show this data in logs
def log_data(data: dict) -> str:
    data = data.copy()
    if "input" in data:
        if "image" in data["input"] or "img" in data["input"]:
            data["input"]["image"] = "data:image/jpeg;base64, ..."
    return pformat(data)


@dataclass
class Prediction:
    predict_time: float
    inputs: dict[str, str]
    output: Url
    cost: float


class Replicate:
    api_url: str = "https://api.replicate.com/v1/predictions"

    def __init__(
            self,
            token: str,
            default_inputs: dict[str, str] = None,
            predict_status_timeout: int = 3,
            proxy: str | None = None,
            timeout: int = 5 * 60,
    ):
        self.inputs = default_inputs or {}
        self.proxy = proxy
        self.headers = {
            "Authorization": f"Token {token}"
        }
        self.timeout = timeout
        self.session: aiohttp.ClientSession | None = None
        self.predict_status_timeout = predict_status_timeout

    async def init_session(self):
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        )

    async def __aenter__(self):
        await self.init_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def predict(
            self,
            diffusion_model: ReplicateDiffusionModel,
            prompt: str | None = None,
            extra_inputs: dict[str, str | int] = None,
            cb: typing.Callable[[str], typing.Awaitable[typing.Any]] = None,
    ) -> Prediction:
        inputs = self.inputs | diffusion_model.default_inputs | (extra_inputs or {})
        prompt_field = diffusion_model.prompt_field
        if isinstance(prompt, str):
            _prompt = ""
            if input_field := self.inputs.get(prompt_field):
                _prompt += input_field + ", "
            if def_field := diffusion_model.default_inputs.get(prompt_field):
                _prompt += def_field + ", "
            if extra_inputs and (extra_field := extra_inputs.get(prompt_field)):
                _prompt += extra_field + ", "
            if prompt:
                inputs[prompt_field] = _prompt + prompt
        else:
            inputs[prompt_field] = prompt
            inputs = encode_json(inputs, upload_file)
        data = {
            "version": diffusion_model.version,
            "input": inputs
        }
        async with self.session.post(self.api_url, json=data, proxy=self.proxy) as res:
            logger.info(f"Predicting: {diffusion_model.model=}\n{prompt=}\n{log_data(data)}")
            result = await res.json()
            if "id" not in result:
                logger.error(f"\nS1. Predicted: {diffusion_model.model=}\n{prompt=}\n{pformat(result)}")
                if detail := result.get("detail"):
                    raise Exception(detail)
                raise Exception(result["detail"])
            prediction_url = self.api_url + "/" + result["id"]
            while True:
                await asyncio.sleep(self.predict_status_timeout)
                async with self.session.get(prediction_url, proxy=self.proxy) as res:
                    result = await res.json()
                    logger.debug(f"{pformat(result)}")
                    if result["status"] in ("canceled", "failed"):
                        logger.error(f"\nS2. Predicted: {diffusion_model.model=}\n{prompt=}\n{pformat(result)}")
                        if error := result.get("error"):
                            logger.error(error)
                        raise Exception(
                            f"❌ К сожалению, произошла ошибка при генерации изображения, повторите позже...")
                    try:
                        percent = result["logs"].split("\n")[-2]
                        # find 1 percent
                        percent = re.search(r"\d+%", percent)
                        if percent:
                            percent = percent.group(0)
                            if cb:
                                try:
                                    await cb(percent)
                                except Exception as e:
                                    logger.warning(e)
                    except IndexError:
                        pass
                if result["status"] == "succeeded":
                    logger.success(f"\nS3. Predicted: {diffusion_model.model=}\n{prompt=}\n{pformat(result)}")
                    predict_time = result["metrics"]["predict_time"]
                    return Prediction(
                        inputs=inputs,
                        predict_time=predict_time,
                        output=diffusion_model.parse_output(result),
                        cost=predict_time * diffusion_model.cost,
                    )
                if result["status"] == "failed":
                    logger.error(f"\nPredicted: {diffusion_model.model=}\n{prompt=}\n{pformat(result)}")
                    if error := result.get("error"):
                        logger.error(error)
                    raise Exception(f"❌ К сожалению, произошла ошибка при генерации изображения, повторите позже...")


async def cb(percent):
    print(f"\r{percent}", end="")


async def main():
    token = "***REMOVED***"
    token = "***REMOVED***"
    # with  as file:
    #     file = io.BytesIO(file.read())
    # file.name = "screenshot.jpg"
    # file.seek(0)
    file = open("screenshot.png", "rb")
    # print(file.tell())
    async with Replicate(token=token, predict_status_timeout=1) as replicate:
        diffusion_model = ReplicateDiffusionModel(
            type=DiffusionType.IMAGE_TO_IMAGE,
            model="j-min/clip-caption-reward:de37751f75135f7ebbe62548e27d6740d5155dfefdf6447db35c9865253d7e06",
            prompt_field="image",
            # default_inputs={
            #     "reward": "clips_grammar"
            # }
        )
        prediction = await replicate.predict(diffusion_model, prompt=file, cb=cb)
        # print(prediction)


if __name__ == '__main__':
    asyncio.run(main())
