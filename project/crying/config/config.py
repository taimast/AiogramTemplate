import os
import ssl
import zoneinfo
from pathlib import Path
from typing import Optional

import yaml
from aiogram.types import FSInputFile
from pydantic import BaseModel, BaseSettings, Field, SecretStr, validator, FilePath
from pydantic.env_settings import InitSettingsSource, EnvSettingsSource, SecretsSettingsSource

from project.crying.config.merchant import Qiwi, Yookassa, CryptoCloud

BASE_DIR = Path(__file__).parent.parent.parent
LOG_DIR = BASE_DIR / "logs"
MEDIA_DIR = BASE_DIR / 'media'

for DIR in [LOG_DIR, MEDIA_DIR]:
    DIR.mkdir(exist_ok=True)

I18N_DOMAIN = "crying"
LOCALES_DIR = BASE_DIR / "project/crying/apps/bot/locales"
TIME_ZONE = zoneinfo.ZoneInfo("Europe/Moscow")
MODELS_DIR = "project.crying.db.models"

PAYMENT_LIFETIME = 60  # minutes

DEBUG = os.getenv("DEBUG")


def load_yaml(file) -> dict:
    with open(Path(BASE_DIR, file), "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def yaml_settings(settings: BaseSettings) -> dict:
    return load_yaml(settings.__config__.config_file)


class Bot(BaseModel):
    token: SecretStr
    admins: list[int] = Field(default_factory=list)


class SSL(BaseModel):
    certfile: FilePath
    keyfile: FilePath

    def get_certfile(self) -> FSInputFile:
        # return open(self.certfile, "rb")
        return FSInputFile(self.certfile)

    def get_ssl_context(self) -> Optional[ssl.SSLContext]:
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(self.certfile, self.keyfile)
        return ssl_context


class Webhook(BaseModel):
    domain: str
    path: Optional[str]
    host: str = "0.0.0.0"
    port: int = 9000

    ssl_cert: Optional[SSL]

    @validator("path", always=True, )
    def webhook_path_validator(cls, v, values):
        if v is None:
            # return "/webhook/{}".format(values["token"])
            return "/webhook/bot"

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


class Database(BaseModel):
    user: str
    password: SecretStr
    database: str
    host: str
    port: int

    @property
    def url(self):
        return f"postgres://{self.user}:{self.password.get_secret_value()}@{self.host}:{self.port}/{self.database}"


class MerchantGroup(BaseModel):
    qiwi: Optional[Qiwi]
    yookassa: Optional[Yookassa]
    crypto_cloud: Optional[CryptoCloud]


class Settings(BaseSettings):
    bot: Bot
    webhook: Optional[Webhook]
    db: Database
    merchants: Optional[MerchantGroup]

    class Config:
        env_file = r"..\..\.env" if DEBUG else r"..\..\.env_dev"
        env_file_encoding = "utf-8"
        config_file = "config.yaml" if DEBUG else "config_dev.yaml"
        case_sensitive = True

        @classmethod
        def customise_sources(cls,
                              init_settings: InitSettingsSource,
                              env_settings: EnvSettingsSource,
                              file_secret_settings: SecretsSettingsSource):
            return init_settings, env_settings, yaml_settings, file_secret_settings


config = Settings()
