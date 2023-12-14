from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from aiogram import types, Bot
from aiogram.utils import markdown as md
from loguru import logger

from diffusion_bot.apps.bot.keyboards.common import common_kbs

if TYPE_CHECKING:
    from diffusion_bot.locales.stubs.ru.stub import TranslatorRunner
    from .midjourney import MidjourneyWorker

UserID = int


class MJQueueManager:
    semaphore: asyncio.Semaphore = asyncio.Semaphore(100)
    managers: dict[UserID, MJQueueManager] = {}
    queue_tasks: dict[UserID, asyncio.Task] = {}

    def __init__(
            self,
            user_id: UserID,
            edit_message: types.Message,
            bot:Bot,
            l10n: TranslatorRunner,
            mj_worker: MidjourneyWorker,
            release_delay: int = 60 * 8
    ):
        self.user_id = user_id
        self.edit_message = edit_message
        self.bot = bot
        self.place_in_queue = len(self.semaphore._waiters) if self.semaphore._waiters else 1
        self.l10n = l10n
        self.mj_worker = mj_worker

        self.trigger_id: str | None = None
        self.prompt: str | None = None

        self._progress_task: asyncio.Task | None = None
        self._release_task: asyncio.Task | None = None
        self.release_delay = release_delay

        self.can_cancel = True
        self.released = False
        self.queue_reduced = False

    @classmethod
    def get_manager(cls, user_id: int) -> MJQueueManager | None:
        return cls.managers.get(user_id)

    @classmethod
    def get_manager_by_trigger_id(cls, trigger_id: str) -> MJQueueManager | None:
        for manager in cls.managers.values():
            if manager.trigger_id == trigger_id:
                return manager
        return None

    def add_queue_task(self, task: asyncio.Task):
        self.queue_tasks[self.user_id] = task

    @classmethod
    def get_queue_task(cls, user_id: int) -> asyncio.Task | None:
        return cls.queue_tasks.get(user_id)

    @classmethod
    async def try_create(
            cls,
            user_id: int,
            edit_message: types.Message,
            l10n: TranslatorRunner,
            mj_worker: MidjourneyWorker,
    ) -> MJQueueManager | None:
        bot = Bot.get_current()
        if mj_queue_manager := cls.managers.get(user_id):
            if mj_queue_manager.can_cancel:
                await bot.edit_message_text(
                    l10n.diffusion.midjourney.queue.want_cancel(),
                    user_id,
                    edit_message.message_id,
                    reply_markup=common_kbs.mj_want_cancel(l10n)
                )
            else:
                await bot.edit_message_text(
                    l10n.diffusion.midjourney.queue.cannot_cancel(),
                    user_id,
                    edit_message.message_id,
                )
            return None
        mj_queue_manager = MJQueueManager(user_id, edit_message,bot, l10n, mj_worker)
        cls.managers[user_id] = mj_queue_manager
        return mj_queue_manager

    async def realtime_progress(self):
        wait_time_text = self.l10n.diffusion.midjourney.queue.wait_time()
        position_text = self.l10n.diffusion.midjourney.queue.position()
        counter = 0
        sleep_time = 3
        reply_markup = common_kbs.mj_want_cancel(self.l10n)
        while True:
            counter += sleep_time
            try:
                w_text = f"{wait_time_text} {md.hcode(counter)}s"
                rm = None
                if self.can_cancel:
                    w_text = f"{position_text} {md.hcode(self.place_in_queue)}\n{w_text}"
                    rm = reply_markup
                await self.bot.edit_message_text(w_text, self.user_id, self.edit_message.message_id, reply_markup=rm)
            except Exception as e:
                logger.warning(e)
                await asyncio.sleep(sleep_time)
            await asyncio.sleep(sleep_time)
            if counter > 600:
                break

    def _reduce_queues(self):
        if self.queue_reduced:
            return False
        for manager in list(self.managers.values()):
            if manager.user_id != self.user_id:
                manager.place_in_queue -= 1
        self.queue_reduced = True
        return True

    def release(self) -> bool:
        if self.released:
            return False
        self.released = True
        if self._progress_task:
            self._progress_task.cancel()
        if self._release_task:
            self._release_task.cancel()

        self._reduce_queues()

        del self.managers[self.user_id]
        del self.queue_tasks[self.user_id]
        self.semaphore.release()

        logger.info(f"User {self.user_id} released lock")
        return True

    def cancel(self) -> bool:
        if not self.can_cancel:
            return False
        self.can_cancel = False
        self.queue_tasks[self.user_id].cancel()
        del self.queue_tasks[self.user_id]

        if self._progress_task:
            self._progress_task.cancel()
        self._reduce_queues()
        del self.managers[self.user_id]
        return True

    def set_trigger_id(self, trigger_id: str):
        self.trigger_id = trigger_id

    def set_prompt(self, prompt: str):
        self.prompt = prompt

    async def release_trigger(self):
        if self.trigger_id:
            try:
                result = await self.mj_worker.release(self.trigger_id)
                pt = self.mj_worker.cache.get_processing_trigger(self.trigger_id)
                await self.bot.delete_message(
                    chat_id=pt.user_id,
                    message_id=pt.message_id,
                )
                logger.info(f"Release callback trigger {self.trigger_id} for user:{self.user_id}: {result}")
            except Exception as e:
                logger.warning(f"Release callback trigger {self.trigger_id} for user:{self.user_id}: {e}")

    async def delayed_release(self):
        await asyncio.sleep(self.release_delay)
        release = self.release()
        if release:
            logger.info(f"User {self.user_id} released after {self.release_delay} seconds")
            await self.bot.send_message(self.user_id, self.l10n.diffusion.predicting.timeout())
            # await self.release_trigger()

    @classmethod
    async def release_by_banned_words(cls, words: list[str]):
        released = 0
        managers_for_release = []
        for manager in cls.managers.values():
            if manager.prompt in words:
                managers_for_release.append(manager)

        for manager in managers_for_release:
            await manager.banned_release(manager.prompt)
            released += 1

        if released:
            logger.info(f"Released {released} users by banned words: {words}")
        else:
            logger.warning(f"No users released by banned words: {words}")

    async def banned_release(self, text: str):
        self.release()
        logger.info(f"User {self.user_id} released when banned: {text}")
        # diffusion-midjourney-prompt-banned
        await self.bot.send_message(self.user_id, self.l10n.diffusion.midjourney.prompt.banned())
        await self.release_trigger()

    def _after_semaphore(self):
        self.can_cancel = False
        self._reduce_queues()
        self._release_task = asyncio.create_task(self.delayed_release())

    # подождать своей очереди
    async def wait(self):
        self._progress_task = asyncio.create_task(self.realtime_progress())
        logger.info(f"User {self.user_id} wait for semaphore")
        await self.semaphore.acquire()
        logger.info(f"User {self.user_id} acquired semaphore")
        self._after_semaphore()

    async def __aenter__(self):
        try:
            await self.wait()
        except Exception as e:
            logger.exception(e)
            self.release()
        except (asyncio.CancelledError, asyncio.TimeoutError):
            self.release()
            raise

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # release only if exception
        logger.info(f"User {self.user_id} exit from context manager")
        if exc_type:
            self.release()
