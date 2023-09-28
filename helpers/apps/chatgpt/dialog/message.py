from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from enum import StrEnum

from aiogram import md
from aiogram.utils import markdown as md


class Role(StrEnum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class Message:
    role: Role
    content: str
    datetime: str = field(default_factory=lambda: datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"))

    def pretty(self):
        role = f"[{self.role}]"
        return f"{md.hcode(role)}\n{self.content}"

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            role=data['role'],
            content=data['content'],
            datetime=data.get('datetime')
        )

    def to_dict(self, exclude_datetime=True):
        data = {
            'role': self.role,
            'content': self.content,
        }
        if not exclude_datetime:
            data['datetime'] = self.datetime
        return data
