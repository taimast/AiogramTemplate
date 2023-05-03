from pathlib import Path
from typing import Optional

from aiogoogle.auth.creds import ServiceAccountCreds
from pydantic import BaseModel, Field, validator

BASE_DIR = Path(__file__).parent.parent.parent


class GoogleSheets(BaseModel):
    spreadsheet_id: str
    scopes: list[str] = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials_file: Path = Field(default_factory=lambda: BASE_DIR / "credentials.json")
    credentials: Optional[ServiceAccountCreds] = None

    @validator("credentials", always=True)
    def validate_credentials(cls, value, values):
        if not value:
            credentials_file = values.get("credentials_file")
            scopes = values.get("scopes")
            return ServiceAccountCreds(**load_yaml(credentials_file), scopes=scopes)
        return value
