from typing import Any, Awaitable, Callable

import sqlalchemy
from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import CallbackQuery, Message
from loguru import logger

from src.db.models import User
from src.db.models.user.light import LightUser
from src.db.persistence_session.manager import PersistenceSessionManager


class LightUserMiddleware(BaseMiddleware):
    def __init__(
        self,
        session_manager: PersistenceSessionManager[str],
    ):
        self.session_manager = session_manager

    async def __call__(  # type: ignore
        self,
        handler: Callable[[Message | CallbackQuery, dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: dict[str, Any],
    ) -> Any:
        user = event.from_user
        if not user:
            return await handler(event, data)
        print(data["event_from_user"], "EVENT_FROM_USER")
        # TODO: Использоваь pipeline для блокировки вставки при множетсвенных запросах
        exists = await self.session_manager.light.exists(LightUser, LightUser.make_key(user.id))

        if not exists:
            logger.debug("Light user for User {} not found", user.id)
            tg_user_data = user.model_dump(exclude={"language_code"})
            rich_user = User()
            rich_user.update(**tg_user_data)
            light_user = LightUser.from_tg_user(user).as_(self.session_manager)
            try:
                await LightUser.create_rich(rich_user, self.session_manager)
            except sqlalchemy.exc.IntegrityError as e:
                logger.warning("User already exists in rich: {}", e)
            await LightUser.create_light(self.session_manager, light_user)

        light_user_flag = get_flag(data, "light_user")
        if light_user_flag:
            logger.debug("Get light user for User {}", user.id)

            light_user = await LightUser.get_light(self.session_manager, user.id)
            data["light_user"] = light_user

            if isinstance(light_user_flag, dict):
                if light_user_flag.get("with_rich"):
                    async with light_user.with_rich() as rich_user:
                        data["user"] = rich_user
                        return await handler(event, data)

        return await handler(event, data)
