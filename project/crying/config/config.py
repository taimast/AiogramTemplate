import zoneinfo
from pathlib import Path
from typing import Optional, Any, Callable

import yaml
from pydantic import BaseModel, BaseSettings, Field, SecretStr
from pydantic.env_settings import InitSettingsSource, EnvSettingsSource, SecretsSettingsSource

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


def yaml_settings(settings: BaseSettings) -> dict:
    return load_yaml(settings.__config__.config_file)


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


# class MerchantGroup(BaseModel):
#     qiwi: Optional[Qiwi]
#     yookassa: Optional[Yookassa]
#     crypto_cloud: Optional[CryptoCloud]


class Settings(BaseSettings):
    bot: Bot
    webhook: Optional[Webhook]
    db: Database

    # merchants: Optional[MerchantGroup]

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

