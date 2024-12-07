from redis.asyncio import Redis

from src.db.persistence_session.manager import PersistenceSessionManager
from src.db.persistence_session.memory import MemoryPersistenceSession
from src.db.persistence_session.redis import RedisPersistenceSession
from src.setup.opts import SetupOpts


async def setup_session_manager(opts: SetupOpts) -> PersistenceSessionManager:
    if opts.settings.redis:
        redis = Redis.from_url(url=opts.settings.redis.url)
        light_persistence_session = RedisPersistenceSession(redis)
    else:
        light_persistence_session = MemoryPersistenceSession()

    session_manager = PersistenceSessionManager(
        db_sessionmaker=opts.session_maker,
        light=light_persistence_session,
    )
    await session_manager.initialize_light_cache()

    return session_manager
