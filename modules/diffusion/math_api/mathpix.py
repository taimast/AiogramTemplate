import asyncio
import base64
from dataclasses import dataclass
from pprint import pprint
from typing import ClassVar, Any

import aiohttp
from loguru import logger


@dataclass
class MathPix:
    url: ClassVar[str] = "https://api.mathpix.com/v3/text"
    app_id: str
    app_key: str
    session: Any = None

    def init_session(self):
        self.session = aiohttp.ClientSession(headers={
            "app_id": self.app_id,
            "app_key": self.app_key
        })

    async def __aenter__(self):
        self.init_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def predict(self, photo: bytes) -> str:
        src = base64.b64encode(photo).decode('utf-8')
        src = f"data:image/png;base64,{src}"
        json = {
            "src": src,
            "formats": ["text"],
            "data_options": {
                "include_asciimath": True,
                # "include_latex": True
            }
        }
        async with self.session.post(self.url, json=json) as res:
            result = await res.json()
            return result.get("text")


async def main():
    # print(url)
    with open("img.png", "rb") as f:
        photo = f.read()
        src = base64.b64encode(photo).decode('utf-8')
        src = f"data:image/png;base64,{src}"
        # src = await save_photo(f)
        # print(src)
        pass
    # base64_photo = base64.b64encode(photo)
    json = {
        "src": src,
        # "src": "https://mathpix-ocr-examples.s3.amazonaws.com/cases_hw.jpg",
        "formats": ["text", "data", "html"],
        "data_options": {
            "include_asciimath": True,
            # "include_latex": True
        }
    }
    headers = {
        "app_id": "pacmanbotai_gmail_com_e98796_e16211",
        "app_key": "f707dc9f517e0e7add256ed0256db9cf20868143d2fd64118b5bdfeca147d4f9"
    }
    url = "https://api.mathpix.com/v3/text"
    logger.info("Start request")
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post(url, json=json) as res:
            result = await res.json()
            pprint(result)


if __name__ == '__main__':
    asyncio.run(main())
