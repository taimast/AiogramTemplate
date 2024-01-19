from typing import Self

from pydantic import BaseModel, SecretStr


class PostgresDB(BaseModel):
    user: str = "postgres"
    password: SecretStr = SecretStr("postgres")
    database: str
    host: str = "localhost"
    port: int = 5432
    timezone: str = "Europe/Moscow"
    dialect: str = "asyncpg"

    def __str__(self):
        return f"{self.database}[{self.host}]"

    @property
    def url(self):
        return (f"postgresql+{self.dialect}://"
                f"{self.user}:{self.password.get_secret_value()}"
                f"@{self.host}:{self.port}"
                f"/{self.database}")

    @property
    def sqlite_url(self):
        return f"sqlite+aiosqlite:///{self.database}.db"

    @property
    def sync_url(self):
        return (f"postgresql://"
                f"{self.user}:{self.password.get_secret_value()}"
                f"@{self.host}:{self.port}"
                f"/{self.database}")

    @classmethod
    def default(cls) -> Self:
        return cls(
            user="postgres",
            password="postgres",
            database="src",
        )
