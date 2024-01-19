import ssl
from typing import Optional

from aiogram.types import FSInputFile
from pydantic import BaseModel, validator, FilePath


class SSL(BaseModel):
    certfile: FilePath
    keyfile: FilePath

    def get_certfile(self) -> FSInputFile:
        return FSInputFile(self.certfile)

    def get_ssl_context(self) -> Optional[ssl.SSLContext]:
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(self.certfile, self.keyfile)
        return ssl_context


class Webhook(BaseModel):
    domain: str
    path: Optional[str]
    host: str = "0.0.0.0"
    port: int = 443

    ssl_cert: Optional[SSL]

    @validator("path", always=True, )
    def webhook_path_validator(cls, v, values):
        if v is None:
            return "/webhook/bot/{}".format(values["token"])
            # return "/webhook/bot"

        if v.startswith("/"):
            return v
        return "/" + v

    @property
    def url(self):
        return f"{self.domain}{self.path}"

    def get_ssl_context(self) -> Optional[ssl.SSLContext]:
        if self.ssl_cert:
            return self.ssl_cert.get_ssl_context()
        return

    def get_certfile(self) -> Optional[FSInputFile]:
        if self.ssl_cert:
            return self.ssl_cert.get_certfile()
        return
