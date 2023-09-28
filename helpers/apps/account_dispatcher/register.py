from dataclasses import dataclass

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.models import User, Account
from .dispatcher import Dispatcher


async def register_account(session: AsyncSession, dispatcher: Dispatcher, user: User):
    """ Register account. Can raise DispatcherRegistrationError """

    logger.info("Registering account")
    async with dispatcher as dispatcher:
        user = await dispatcher.client.get_me()
        account = Account(
            api_id=dispatcher.account.api_id,
            api_hash=dispatcher.account.api_hash,
            phone_number=dispatcher.account.phone_number,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
        )
        await dispatcher.db.add(account)
        await dispatcher.db.commit()
    logger.info(f"Account {dispatcher.account.api_id} registered")
    return account


@dataclass
class RegisterDispatcher:
    dispatcher: Dispatcher
    account: Account

    async def register(self):
        """ Register account. Can raise DispatcherRegistrationError """

        logger.info("Registering account")
        async with self.dispatcher as dispatcher:
            user = await dispatcher.client.get_me()
        logger.info(f"Account {dispatcher.account.api_id} registered")
        return self.dispatcher.account
