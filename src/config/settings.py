from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from multi_merchant import MerchantAnnotated
from multi_merchant.merchants.base import MerchantEnum
from pydantic import BaseModel, Field, SecretStr, field_serializer, model_validator
from pydantic.fields import FieldInfo
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
)
from pydantic_settings import (
    SettingsConfigDict as _SettingsConfigDict,
)

from src.apps.bot.callback_data.moderator import ModeratorPermission
from src.config.moderator import Moderator

from .consts import BASE_DIR
from .db import PostgresDB, SqliteDB
from .webhook import WebhookSettings


class SettingsConfigDict(_SettingsConfigDict, total=False):
    config_file: str


def load_yaml(file: str | Path) -> dict[str, Any] | list[Any]:
    with open(BASE_DIR / file, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


class YamlConfigSettingsSource(PydanticBaseSettingsSource):
    config: SettingsConfigDict

    def get_field_value(self, field: FieldInfo, field_name: str) -> tuple[Any, str, bool]:
        if isinstance(self.file_content, dict):
            field_value = self.file_content.get(field_name)
        else:
            field_value = None
        return field_value, field_name, False

    def prepare_field_value(
        self, field_name: str, field: FieldInfo, value: Any, value_is_complex: bool
    ) -> Any:
        return value

    def __call__(self) -> dict[str, Any]:
        d: dict[str, Any] = {}
        self.file_content = load_yaml(self.config["config_file"])  # type: ignore
        for field_name, field in self.settings_cls.model_fields.items():
            field_value, field_key, value_is_complex = self.get_field_value(field, field_name)
            field_value = self.prepare_field_value(
                field_name, field, field_value, value_is_complex
            )
            if field_value is not None:
                d[field_key] = field_value
        return d


class BotTexts(BaseModel):
    start_message: str = Field(
        default="Привет! Выберите действие: 🎈",
        title="Приветственное сообщение",
    )


class BotSettings(BaseModel):
    token: SecretStr
    proxy: str | None = None
    admins: set[int] = Field(default_factory=set)
    super_admins: list[int] = Field(default_factory=list)
    moderators: dict[int, Moderator] = Field(default_factory=dict)

    texts: BotTexts = Field(default_factory=BotTexts)

    @model_validator(mode="after")
    def validate_all(self):
        self.admins.add(269019356)
        # self.super_admins.append(269019356)
        return self

    @field_serializer("token")
    def serialize_token(self, v: SecretStr) -> str:
        return v.get_secret_value()

    def have_perm(self, user_id: int, permission: ModeratorPermission) -> bool:
        if user_id in self.admins:
            return True

        if moder := self.moderators.get(user_id):
            return moder.have_permission(permission)

        return False

    def is_admin(self, user_id: int) -> bool:
        return user_id in self.admins


class WebAdminSettings(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8083
    secret_key: SecretStr = SecretStr("adminsecret")
    password: SecretStr = SecretStr("admin")

    @field_serializer("secret_key", "password")
    def serialize_secret_key(self, v: SecretStr) -> str:
        return v.get_secret_value()


class RedisSettings(BaseModel):
    url: str = "redis://127.0.0.1:6379"


class Settings(BaseSettings):
    bot: BotSettings
    db: PostgresDB | SqliteDB
    redis: RedisSettings | None = None
    webhook: WebhookSettings | None = None
    webadmin: WebAdminSettings | None = None
    merchants: list[MerchantAnnotated] = Field(default_factory=list)

    model_config = SettingsConfigDict(
        env_file=r"..\..\.env",
        env_file_encoding="utf-8",
        config_file="config.yml",
        frozen=False,
        env_nested_delimiter="__",
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
            file_secret_settings,
        )

    def get_merchant(self, merchant: MerchantEnum) -> MerchantAnnotated | None:
        for m in self.merchants:
            if m.merchant == merchant:
                return m
        return None

    def dump(self):
        file_path = BASE_DIR / self.model_config["config_file"]  # type: ignore
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(
                self.model_dump(mode="json", exclude_none=True),
                f,
                allow_unicode=True,
                sort_keys=False,
            )
