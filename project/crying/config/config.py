from __future__ import annotations

import zoneinfo
from pathlib import Path
from typing import Optional, Any, Callable

import yaml
from pydantic import BaseModel, BaseSettings, Field, SecretStr, validator
from pydantic.env_settings import InitSettingsSource, EnvSettingsSource, SecretsSettingsSource

from .db import SqliteDB, PostgresDB
from .webhook import Webhook
from ..apps.merchant import MerchantAnnotated

BASE_DIR = Path(__file__).parent.parent.parent
LOG_DIR = BASE_DIR / "logs"
MEDIA_DIR = BASE_DIR / 'media'

for DIR in [LOG_DIR, MEDIA_DIR]:
    DIR.mkdir(exist_ok=True)

LOCALES_DIR = BASE_DIR / "crying/locales"
TIME_ZONE = zoneinfo.ZoneInfo("Europe/Moscow")


def load_yaml(file: str | Path) -> dict[str, Any] | list[Any]:
    with open(BASE_DIR / file, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


class Bot(BaseModel):
    token: SecretStr
    admins: list[int] = Field(default_factory=list)
    super_admins: list[int] = Field(default_factory=list)

    @validator("admins", "super_admins")
    def validate_admins(cls, v):
        return v or []


class Settings(BaseSettings):
    bot: Bot
    db: PostgresDB | SqliteDB
    webhook: Optional[Webhook]
    merchants: list[MerchantAnnotated] = Field(default_factory=list)

    class Config:
        env_file = r"..\..\.env"
        env_file_encoding = "utf-8"
        config_file = "config.yml"
        allow_mutation = False
        env_nested_delimiter = '__'

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

    def dump(self):
        with open(BASE_DIR / self.__config__.config_file, "w", encoding="utf-8") as f:
            data = self.dict()

            def if_merchants(obj, k, v):
                if k == "merchants":
                    merchants = []

                    for merchant in v:
                        merchants.append(
                            {"merchant": str(merchant["merchant"]),
                             "shop_id": merchant["shop_id"],
                             "api_key": merchant["api_key"].get_secret_value(),
                             }
                        )
                    obj[k] = merchants

            def recursive_remove_secret(obj):
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        if k == "merchants":
                            if_merchants(obj, k, v)
                        elif isinstance(v, SecretStr):
                            obj[k] = v.get_secret_value()
                        else:
                            recursive_remove_secret(v)
                elif isinstance(obj, list):
                    for v in obj:
                        recursive_remove_secret(v)

            recursive_remove_secret(data)
            yaml.dump(data, f, allow_unicode=True, sort_keys=False)
