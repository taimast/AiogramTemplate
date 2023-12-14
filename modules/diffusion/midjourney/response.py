from __future__ import annotations

from dataclasses import dataclass
from typing import TypedDict, List, Callable

from charset_normalizer.md import Optional

from diffusion_bot.apps.bot.callback_data.midjourney import MidjourneyAction
from diffusion_bot.apps.diffusion.midjourney.request import MJRequest

TriggerID = str
MsgID = UserID = MessageID = int


@dataclass
class ProcessingTrigger:
    trigger_id: TriggerID
    user_id: UserID
    message_id: MessageID
    unlocker: Optional[Callable] = None
    action: MidjourneyAction = MidjourneyAction.VARIATION

    def __post_init__(self):
        if isinstance(self.action, str):
            self.action = MidjourneyAction(self.action)

    @classmethod
    def from_request(cls, request: MJRequest):
        return cls(
            request.trigger_id,
            request.user.id,
            request.message.message_id,
            request.unlocker,
            request.action
        )

    def release(self):
        if self.unlocker:
            self.unlocker()


@dataclass
class Trigger:
    msg_id: MsgID
    msg_hash: str
    trigger_id: TriggerID
    prompt: str = ""

    @classmethod
    def from_callback_data(cls, callback_data: CallbackData):
        filename = callback_data["attachments"][0]["filename"]
        msg_hash = filename.split("_")[-1].split(".")[0]
        msg_id = callback_data["id"]
        trigger_id = callback_data["trigger_id"]
        return cls(msg_id, msg_hash, trigger_id)


class BannedWordsResult(TypedDict):
    words: list[str]


class Attachment(TypedDict):
    id: int
    url: str
    proxy_url: str
    filename: str
    content_type: str
    width: int
    height: int
    size: int
    ephemeral: bool


class EmbedsImage(TypedDict):
    url: str
    proxy_url: str


class Embed(TypedDict):
    type: str
    description: str
    image: EmbedsImage


class CallbackData(TypedDict):
    type: str
    id: int
    content: str
    attachments: List[Attachment]
    embeds: List[Embed]

    trigger_id: str
