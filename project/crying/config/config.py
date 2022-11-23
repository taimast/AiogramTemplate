import zoneinfo
from pathlib import Path
from pprint import pprint
from typing import Optional, Any, Callable

import yaml
from pydantic import BaseModel, BaseSettings, Field, SecretStr, root_validator
from pydantic.env_settings import InitSettingsSource, EnvSettingsSource, SecretsSettingsSource

from .merchant.base import Merchant
from .webhook import Webhook

BASE_DIR = Path(__file__).parent.parent.parent
LOG_DIR = BASE_DIR / "logs"
MEDIA_DIR = BASE_DIR / 'media'

for DIR in [LOG_DIR, MEDIA_DIR]:
    DIR.mkdir(exist_ok=True)

I18N_DOMAIN = "crying"
LOCALES_DIR = BASE_DIR / "crying/apps/bot/locales"
TIME_ZONE = zoneinfo.ZoneInfo("Europe/Moscow")
MODELS_DIR = "project.crying.db.models"


def load_yaml(file: str | Path) -> dict[str, Any] | list[Any]:
    with open(BASE_DIR / file, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)



class Bot(BaseModel):
    token: SecretStr
    admins: list[int] = Field(default_factory=list)


class Database(BaseModel):
    user: str
    password: SecretStr
    database: str
    host: str
    port: int
    timezone: str = "Europe/Moscow"

    @property
    def url(self):
        return (f"postgres://"
                f"{self.user}:{self.password.get_secret_value()}"
                f"@{self.host}:{self.port}"
                f"/{self.database}")


# todo L1 23.11.2022 5:27 taima: Подумать что делать с этим
class MerchantGroup(BaseModel):
    qiwi: Optional[Merchant]
    yookassa: Optional[Merchant]
    crypto_cloud: Optional[Merchant]

    @root_validator(pre=True)
    def validate_merchants(cls, values):
        try:
            if qiwi := values.get("qiwi"):
                from .merchant.qiwi import Qiwi
                values["qiwi"] = Qiwi(**qiwi)
            if yookassa := values.get("yookassa"):
                from .merchant.yookassa import Yookassa
                values["yookassa"] = Yookassa(**yookassa)
            if crypto_cloud := values.get("crypto_cloud"):
                from .merchant.crypto_cloud import CryptoCloud
                values["crypto_cloud"] = CryptoCloud(**crypto_cloud)
        except ImportError as e:
            raise ImportError(f"Don't forget to install extra requirements for merchant: {e.name}")
        return values


class Settings(BaseSettings):
    bot: Bot
    webhook: Optional[Webhook]
    db: Database
    merchant: Optional[MerchantGroup]

    class Config:
        env_file = r"..\..\.env"
        env_file_encoding = "utf-8"
        config_file = "config.yaml"
        case_sensitive = True

        @classmethod
        def customise_sources(
                cls,
                init_settings: InitSettingsSource,
                env_settings: EnvSettingsSource,
                file_secret_settings: SecretsSettingsSource
        ) -> tuple[InitSettingsSource, EnvSettingsSource, Callable, SecretsSettingsSource]:
            return (
                init_settings,
                env_settings,
                lambda s: load_yaml(BASE_DIR / s.__config__.config_file),
                file_secret_settings
            )

