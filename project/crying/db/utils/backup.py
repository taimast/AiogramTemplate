import asyncio
import collections
import json

from loguru import logger

from project.crying.config.config import BASE_DIR
from project.crying.db import init_db
from project.crying.db.models import User

backup_name = f"db_backup"
BACKUP_DIR = BASE_DIR / "backup"
BACKUP_DIR.mkdir(exist_ok=True)


async def making_backup():
    logger.debug("Резервное копирование запущено")
    data = collections.defaultdict(list)

    # for model_str in models.__all__:
    for model in [User]:
        # model = getattr(models, model_str)
        for obj in await model.all():
            data[model.__name__].append(dict(obj))

    with open(BACKUP_DIR / f"{backup_name}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, sort_keys=True, indent=4, ensure_ascii=False, default=str)

    logger.info(f"Резервное копирование завершено {backup_name}")


async def main():
    await init_db()
    await making_backup()


if __name__ == "__main__":
    asyncio.run(main())
