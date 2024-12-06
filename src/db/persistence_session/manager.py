from dataclasses import dataclass

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.db.models import User as RichUser
from src.db.persistence_session.base import BasePersistenceSession


@dataclass(frozen=True)
class PersistenceSessionManager[LightKeyT, LightModelT]:
    db_sessionmaker: async_sessionmaker[AsyncSession]
    light: BasePersistenceSession[LightKeyT, LightModelT]

    async def initialize(self):
        from src.db.models.user.light import LightUser

        async with self.db_sessionmaker() as session:
            users = await RichUser.all(session)
            light_users = [user.get_light() for user in users]
            objects = [(user.key, user) for user in light_users]
            if light_users:
                await self.light.set_many(LightUser, objects)  # type: ignore
                logger.info("Light users initialized")
