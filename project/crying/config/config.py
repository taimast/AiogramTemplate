import os
import zoneinfo
from pathlib import Path

import yaml
from pydantic import BaseModel, BaseSettings, Field, SecretStr
from pydantic.env_settings import InitSettingsSource, EnvSettingsSource, SecretsSettingsSource

BASE_DIR = Path(__file__).parent.parent.parent
LOG_DIR = BASE_DIR / "logs"
MEDIA_DIR = BASE_DIR / 'media'
LOG_DIR.mkdir(exist_ok=True)
MEDIA_DIR.mkdir(exist_ok=True)

I18N_DOMAIN = "crying"
LOCALES_DIR = BASE_DIR / "project/crying/apps/bot/locales"
TIME_ZONE = zoneinfo.ZoneInfo("Europe/Moscow")
MODELS_DIR = "project.crying.db.models"


def load_yaml(file) -> dict:
    with open(Path(BASE_DIR, file), "r", encoding="utf-8") as f:
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

    @property
    def url(self):
        return f"postgres://{self.user}:{self.password.get_secret_value()}@{self.host}:{self.port}/{self.database}"


class Settings(BaseSettings):
    bot: Bot
    db: Database

    class Config:
        env_file = r"..\..\.env" if not os.getenv("DEBUG") else r"..\..\.env_dev"
        env_file_encoding = "utf-8"
        config_file = "config.yaml" if not os.getenv("DEBUG") else "config_dev.yaml"
        case_sensitive = True

        @classmethod
        def customise_sources(cls,
                              init_settings: InitSettingsSource,
                              env_settings: EnvSettingsSource,
                              file_secret_settings: SecretsSettingsSource):
            return init_settings, env_settings, yaml_settings, file_secret_settings


config = Settings()
