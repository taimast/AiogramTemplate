import os
import time
from pathlib import Path

from loguru import logger

from project.crying.config.config import COMBINER_MEDIA_DIR


## todo L1 14.11.2022 5:39 taima:Перенести скачивание в отдельный класс
#   dowloader и скачивать оттуда для бота и диспетчера


# delete old files from MEDIA_DIR function
def delete_old_files(user_id: int) -> None:
    # todo L1 TODO 20.01.2023 2:37 taima: Может долго работать, если много файлов
    """Delete old files from MEDIA_DIR"""
    # files = sorted(Path(COMBINER_MEDIA_DIR).iterdir(), key=os.path.getctime)
    files = sorted(Path(COMBINER_MEDIA_DIR).iterdir(), key=os.path.getmtime)
    for file in files:
        if file.stat().st_mtime < time.time() - 60 * 60 * 24 * 7:
            file.unlink()
        else:
            break

    if len(files) > 10:
        for file in files[:3]:
            file.unlink()
            logger.info(f"[Delete] Deleted old file {file.name}")
