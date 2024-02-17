from __future__ import annotations

import zoneinfo
from pathlib import Path

PAYMENT_LIFETIME = 60 * 60
TIME_ZONE = zoneinfo.ZoneInfo("Europe/Moscow")

BASE_DIR = Path(__file__).parent.parent.parent
LOG_DIR = BASE_DIR / "logs"
MEDIA_DIR = BASE_DIR / 'media'
DATABASE_DIR = BASE_DIR / "database"
LOCALES_DIR = BASE_DIR / "src/locales"

for DIR in [LOG_DIR, MEDIA_DIR, DATABASE_DIR]:
    DIR.mkdir(exist_ok=True)
