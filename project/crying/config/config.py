from __future__ import annotations

import zoneinfo
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, BaseSettings, Field, SecretStr, validator
from pydantic.fields import FieldInfo
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict as _SettingsConfigDict

from .db import SqliteDB, PostgresDB
from .webhook import Webhook
from ..apps.merchant import MerchantAnnotated


class SettingsConfigDict(_SettingsConfigDict, total=False):
    config_file: str


BASE_DIR = Path(__file__).parent.parent.parent
LOG_DIR = BASE_DIR / "logs"
MEDIA_DIR = BASE_DIR / 'media'
DATABASE_DIR = BASE_DIR / "database"

for DIR in [LOG_DIR, MEDIA_DIR, DATABASE_DIR]:
    DIR.mkdir(exist_ok=True)

LOCALES_DIR = BASE_DIR / "crying/locales"
TIME_ZONE = zoneinfo.ZoneInfo("Europe/Moscow")


def load_yaml(file: str | Path) -> dict[str, Any] | list[Any]:
    with open(BASE_DIR / file, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


class YamlConfigSettingsSource(PydanticBaseSettingsSource):
    config: SettingsConfigDict

    def get_field_value(
            self, field: FieldInfo, field_name: str
    ) -> tuple[Any, str, bool]:
        field_value = self.file_content.get(field_name)
        print(f"{field_value=}")
        return field_value, field_name, False

    def prepare_field_value(
            self, field_name: str, field: FieldInfo, value: Any, value_is_complex: bool
    ) -> Any:
        return value

    def __call__(self) -> dict[str, Any]:
        d: dict[str, Any] = {}
        self.file_content = load_yaml(self.config['config_file'])
        for field_name, field in self.settings_cls.model_fields.items():
            field_value, field_key, value_is_complex = self.get_field_value(
                field, field_name
            )
            field_value = self.prepare_field_value(
                field_name, field, field_value, value_is_complex
            )
            if field_value is not None:
                d[field_key] = field_value
        return d


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
    webhook: Webhook | None = None
    merchants: list[MerchantAnnotated] = Field(default_factory=list)
    model_config = SettingsConfigDict(
        env_file=r"..\..\.env",
        env_file_encoding='utf-8',
        config_file='config.yml',
        frozen=False,
        env_nested_delimiter='__',
    )

    @classmethod
    def settings_customise_sources(
            cls,
            settings_cls: type[BaseSettings],
            init_settings: PydanticBaseSettingsSource,
            env_settings: PydanticBaseSettingsSource,
            dotenv_settings: PydanticBaseSettingsSource,
            file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:

        return (
            init_settings,
            env_settings,
            YamlConfigSettingsSource(settings_cls),
            dotenv_settings,
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
