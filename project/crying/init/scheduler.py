from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger

from ..config import TIME_ZONE


def setup_scheduler() -> AsyncIOScheduler:
    # Init scheduler
    scheduler = AsyncIOScheduler(timezone=TIME_ZONE)

    # Start scheduler
    scheduler.start()

    logger.info("Scheduler setup completed")
    return scheduler
