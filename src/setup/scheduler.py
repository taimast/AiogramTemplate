from apscheduler import AsyncScheduler
from loguru import logger


async def setup_scheduler() -> AsyncScheduler:
    # Init scheduler
    scheduler = await AsyncScheduler().__aenter__()
    logger.info("Scheduler setup completed")

    await scheduler.start_in_background()

    return scheduler
