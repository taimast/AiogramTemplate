# message: Message,
# prompt: str,
# user: User,
# picurl: str | None = None,
# lock: asyncio.Lock = None
from dataclasses import dataclass
from typing import Callable

from aiogram.types import Message

from diffusion_bot.apps.bot.callback_data.midjourney import MidjourneyAction
from diffusion_bot.db.models import User


@dataclass
class MJRequest:
    # all
    message: Message
    user: User
    action: MidjourneyAction

    # imagine
    prompt: str | None = None
    picurl: str | None = None

    # upscale, variation, refresh
    msg_id: int | None = None

    # upscale, variation
    index: int | None = None

    # describe
    filename: str | None = None
    trigger_id: str | None = None

    # all
    unlocker: Callable = None
