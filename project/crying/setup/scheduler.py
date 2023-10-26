from apscheduler import AsyncScheduler
from apscheduler.triggers.interval import IntervalTrigger
from loguru import logger

from ..config import TIME_ZONE



async def setup_scheduler() -> AsyncScheduler:
    # Init scheduler

    async with AsyncScheduler() as scheduler:
        # Add schedules, configure tasks here
        await scheduler.start_in_background()

    logger.info("Scheduler setup completed")
    return scheduler
