from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass, field
from pprint import pformat
from typing import Awaitable
from typing import Union, BinaryIO, TYPE_CHECKING, Callable

import aiohttp
from aiogram import Bot
from aiogram.types import Message, InputMediaPhoto, BufferedInputFile, InputMediaAnimation
from aiohttp import web, FormData
from fluentogram import TranslatorHub
from loguru import logger
from sqlalchemy.ext.asyncio import async_sessionmaker

from diffusion_bot.apps.bot.callback_data.midjourney import MidjourneyAction
from diffusion_bot.apps.bot.keyboards.common import common_kbs
from diffusion_bot.apps.bot.keyboards.common.common_kbs import md
from diffusion_bot.db.models import User
from .cache import MJCache
from .queue_manager import MJQueueManager
from .request import MJRequest
from .response import (
    CallbackData,
    Attachment,
    Trigger,
    ProcessingTrigger,
    Embed,
    TriggerID,
    BannedWordsResult
)

if TYPE_CHECKING:
    from diffusion_bot.locales.stubs.ru.stub import TranslatorRunner

MJClass = Union['MidjourneySeverMixin', 'MidjourneyWorker']

PERCENT_RE = re.compile(r"\((\d+%)")
PROMPT_RE = re.compile(r"#>(.*)\*\*")

# async method
MJActionMethodType = Callable[[MJRequest], Awaitable[TriggerID]]


class MidjourneyServerMixin:
    host: str = "0.0.0.0"
    port: int = 8065
    cb_path: str = "/callback"
    ban_path = "/banned"

    async def start(self: MJClass):
        app = web.Application()
        app.add_routes([web.post(self.cb_path, self.handle_callback)])
        app.add_routes([web.post(self.ban_path, self.handle_banned)])
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host=self.host, port=self.port)
        await site.start()

    async def handle_callback(self, request: web.Request):
        data: CallbackData = await request.json()
        logger.info(pformat(data))
        trigger_id = data["trigger_id"]
        content = data["content"]
        attachments = data.get("attachments")
        if attachments:
            asyncio.create_task(self.update_message_status(
                data,
                trigger_id,
                content,
                attachments[0],
                data.get("type") == "end"
            ))
        elif data.get("embeds"):
            asyncio.create_task(self.send_embed(data["embeds"][0], trigger_id))
        return web.Response(text="ok")

    @classmethod
    async def handle_banned(cls, request: web.Request):
        data: BannedWordsResult = await request.json()
        logger.info(f"Banned Trigger {pformat(data)}")
        await MJQueueManager.release_by_banned_words(data["words"])
        return web.Response(text="ok")

    async def download_file(self: MJClass, url: str):
        async with self.session.get(url) as resp:
            if resp.status == 200:
                return await resp.read()

    async def send_embed(self: MJClass, embed: Embed, trigger_id: TriggerID):
        processing_trigger = self.cache.get_processing_trigger(trigger_id)
        attachment_url = embed["image"]["proxy_url"]
        file_bytes = await self.download_file(attachment_url)
        file = BufferedInputFile(file_bytes, filename="image.jpg")
        media = InputMediaPhoto(
            media=file,
            caption=f"{embed['description']}",
            parse_mode="Markdown",
        )
        await self.bot.edit_message_media(
            media=media,
            message_id=processing_trigger.message_id,
            chat_id=processing_trigger.user_id,
        )

        processing_trigger = self.cache.get_processing_trigger(trigger_id)

        if processing_trigger:
            processing_trigger.release()
            await self.resize_tokens(processing_trigger)

    async def resize_tokens(self: MJClass, pt: ProcessingTrigger):
        cost = pt.action.cost()
        async with self.db_sessionmaker() as session:
            user = await session.get(User, pt.user_id)
            user.tokens -= cost
            await session.commit()
        l10n: TranslatorRunner = self.translator_hub.get_translator_by_locale(user.language_code)
        await self.bot.send_message(
            user.id,
            l10n.dialog.used_tokens(spent_tokens=cost)
        )

    @classmethod
    def parse_status(cls, content: str):
        percentage = PERCENT_RE.search(content)
        prompt = PROMPT_RE.search(content)
        data = {}
        if percentage:
            data["percentage"] = percentage.group(1)
        if prompt:
            data["prompt"] = prompt.group(1)
        return data

    def get_l10n(self: MJClass, user: User) -> TranslatorRunner:
        return self.translator_hub.get_translator_by_locale(user.language_code)

    async def get_l10n_async(self: MJClass, user_id: int) -> TranslatorRunner:
        async with self.db_sessionmaker() as session:
            user = await session.get(User, user_id)
            return self.translator_hub.get_translator_by_locale(user.language_code)

    async def update_message_status(
            self: MJClass,
            data: CallbackData,
            trigger_id: TriggerID,
            content: str,
            attachment: Attachment,
            done: bool = False
    ):
        if not (p_trigger := self.cache.get_processing_trigger(trigger_id)):
            logger.warning(f"Trigger {trigger_id} not found")
            return
        attachment_url = attachment["proxy_url"]
        file_bytes = await self.download_file(attachment_url)
        file = BufferedInputFile(file_bytes, attachment["filename"])

        trigger_stats = self.parse_status(content)
        prompt = trigger_stats.get("prompt")

        l10n = await self.get_l10n_async(p_trigger.user_id)

        if trigger_stats:
            percentage = md.hcode(trigger_stats.get('percentage', ''))
            content = l10n.diffusion.predicting()
            content = f"{md.hitalic(prompt)}\n\n{content} {percentage}"
            parse_mode = "HTML"
        else:
            parse_mode = None

        reply_markup = None

        if done:
            content = l10n.diffusion.predicted()
            content = f"{content}\n" \
                      f"{md.hcode(prompt)}"
            trigger = Trigger.from_callback_data(data)
            if p_trigger.action in (
                    MidjourneyAction.VARIATION, MidjourneyAction.REFRESH, MidjourneyAction.IMAGINE):
                reply_markup = common_kbs.midjourney_attachment_scale(trigger.msg_id)
                trigger.prompt = trigger_stats.get("prompt", "")

            self.cache.set_done_trigger(trigger)
            p_trigger.release()

        media = InputMediaPhoto(
            media=file,
            caption=content,
            parse_mode=parse_mode,
        )
        if p_trigger.action in (MidjourneyAction.VARIATION, MidjourneyAction.REFRESH) and not done:
            file = await self.cache.imagine_animation.get_file_id(self.bot)
            media = InputMediaAnimation(
                media=file,
                caption=content,
                parse_mode=parse_mode,
            )

        await self.bot.edit_message_media(
            media=media,
            message_id=p_trigger.message_id,
            chat_id=p_trigger.user_id,
            reply_markup=reply_markup,
        )

        if done:
            await self.bot.send_document(
                chat_id=p_trigger.user_id,
                document=file,
                reply_to_message_id=p_trigger.message_id,
            )
            await self.resize_tokens(p_trigger)


@dataclass
class MidjourneyWorker(MidjourneyServerMixin):
    base_ulr: str
    bot: Bot
    db_sessionmaker: async_sessionmaker
    translator_hub: TranslatorHub
    cache: MJCache
    tasks: dict[TriggerID, Message] = field(default_factory=dict)
    session: aiohttp.ClientSession | None = None

    async def init_session(self):
        self.session = aiohttp.ClientSession()

    async def send_loading(self, request: MJRequest):

        animation = await self.cache.imagine_animation.get_file_id(self.bot)

        l10n = self.get_l10n(request.user)
        message = await request.message.answer_animation(
            animation=animation,
            caption=l10n.diffusion.predicting(),
        )

        return message

    async def _request(self, path: str, method: str = "POST", **kwargs):
        async with self.session.request(method, f"{self.base_ulr}/{path}", **kwargs) as resp:
            return await resp.json()

    async def _save_trigger(self, request: MJRequest) -> TriggerID:
        trigger_id = request.trigger_id
        processing_trigger = ProcessingTrigger.from_request(request)
        message = await self.send_loading(request)
        processing_trigger.message_id = message.message_id
        self.cache.set_processing_trigger(processing_trigger)
        return trigger_id

    async def imagine(self, request: MJRequest) -> TriggerID:
        trigger_response = await self._request(
            "imagine",
            json={"prompt": request.prompt, "picurl": request.picurl}
        )
        logger.info(pformat(trigger_response))
        if not trigger_response['message'] == "success":
            raise Exception(trigger_response['message'])

        request.trigger_id = trigger_response["trigger_id"]
        return await self._save_trigger(request)

    async def upscale(self, request: MJRequest) -> TriggerID:
        trigger = self.cache.get_done_trigger(request.msg_id)
        trigger_response = await self._request(
            "upscale",
            json={"index": request.index} | trigger.__dict__
        )

        if not trigger_response['message'] == "success":
            raise Exception(trigger_response['message'])

        request.prompt = trigger.prompt
        request.trigger_id = trigger.trigger_id
        return await self._save_trigger(request)

    async def variation(self, request: MJRequest) -> TriggerID:
        trigger = self.cache.get_done_trigger(request.msg_id)
        trigger_response = await self._request(
            "variation",
            json={"index": request.index} | trigger.__dict__
        )
        if not trigger_response['message'] == "success":
            raise Exception(trigger_response['message'])

        request.prompt = trigger.prompt
        request.trigger_id = trigger.trigger_id
        return await self._save_trigger(request)

    async def refresh(self, request: MJRequest) -> TriggerID:
        trigger = self.cache.get_done_trigger(request.msg_id)
        trigger_response = await self._request(
            "reset",
            json=trigger.__dict__
        )
        if not trigger_response['message'] == "success":
            raise Exception(trigger_response['message'])

        request.prompt = trigger.prompt
        request.trigger_id = trigger.trigger_id
        return await self._save_trigger(request)

    async def describe(self, request: MJRequest) -> TriggerID:
        response = await self._request(
            "describe",
            json={
                "upload_filename": request.filename,
                "trigger_id": request.trigger_id
            }
        )
        if not response['message'] == "success":
            raise Exception(response['message'])
        trigger_id = response["trigger_id"]
        request.trigger_id = trigger_id
        return await self._save_trigger(request)

    async def upload(self, filename: str, file: BinaryIO) -> tuple[str, str]:
        data = FormData()
        data.add_field(
            'file',
            file,
            filename=filename,
            content_type='image/jpeg'
        )
        response = await self._request(
            "upload",
            data=data
        )
        if not response['message'] == "success":
            raise Exception(response['message'])

        return response['trigger_id'], response['upload_filename']

    async def release(self, trigger_id: TriggerID):
        response = await self._request(
            "queue/release",
            json={
                "trigger_id": trigger_id
            }
        )
        return response
