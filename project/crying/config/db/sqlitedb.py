from pydantic import BaseModel


class SqliteDB(BaseModel):
    path: str = "crying.db"
    timezone: str = "Europe/Moscow"
    dialect: str = "aiosqlite"

    class Config:
        allow_mutation = False

    def __str__(self):
        return f"Database {self.path}"

    @property
    def url(self):
        return (f"sqlite+{self.dialect}://"
                f"{self.path}")

    @property
    def tortoise_url(self):
        return (f"sqlite://"
                f"{self.path}")
