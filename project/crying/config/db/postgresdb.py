from typing import Self

from pydantic import BaseModel, SecretStr


class PostgresDB(BaseModel):
    user: str
    password: SecretStr
    database: str
    host: str = "localhost"
    port: int = 5432
    timezone: str = "Europe/Moscow"
    dialect: str = "asyncpg"

    class Config:
        allow_mutation = False

    def __str__(self):
        return f"Database {self.database}[{self.host}]"

    @property
    def url(self):
        return (f"postgresql+{self.dialect}://"
                f"{self.user}:{self.password.get_secret_value()}"
                f"@{self.host}:{self.port}"
                f"/{self.database}")

    @property
    def tortoise_url(self):
        return (f"postgres://"
                f"{self.user}:{self.password.get_secret_value()}"
                f"@{self.host}:{self.port}"
                f"/{self.database}")

    @classmethod
    def default(cls) -> Self:
        return cls(
            user="postgres",
            password="postgres",
            database="crying",
        )
