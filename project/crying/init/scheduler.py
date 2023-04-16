from apscheduler.schedulers.asyncio import AsyncIOScheduler

from project.crying.config import TIME_ZONE
from project.crying.utils.backup import making_backup


def setup_scheduler() -> AsyncIOScheduler:
    """Инициализация и запуск планировщика задач."""
    # Инициализация планировщика
    scheduler = AsyncIOScheduler(timezone=TIME_ZONE)

    # Создание бекапа базы данных
    scheduler.add_job(making_backup, 'cron', hour=0, minute=0)

    # Запуск планировщика
    scheduler.start()
    return scheduler
