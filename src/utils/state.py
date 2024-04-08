from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import BaseStorage, DEFAULT_DESTINY, StorageKey
from aiogram.fsm.strategy import apply_strategy


def get_state(
        storage: BaseStorage,
        user_id: int,
        bot: Bot,
        thread_id: int = None,
        destiny: str = DEFAULT_DESTINY
) -> FSMContext:
    chat_id, user_id, thread_id = apply_strategy(
        chat_id=user_id,
        user_id=user_id,
        thread_id=thread_id,
        strategy=DEFAULT_DESTINY,
    )
    return FSMContext(
        storage=storage,
        key=StorageKey(
            user_id=user_id,
            chat_id=chat_id,
            bot_id=bot.id,
            thread_id=thread_id,
            destiny=destiny,
        ),
    )
