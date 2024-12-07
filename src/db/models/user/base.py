from aiogram.utils import markdown
from aiogram.utils.link import create_tg_link
from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base, TimestampMixin


class BaseUser(Base, TimestampMixin):
    __abstract__ = True
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str | None] = mapped_column(String(32), index=True)
    first_name: Mapped[str | None] = mapped_column(String(100))
    last_name: Mapped[str | None] = mapped_column(String(100))
    is_bot: Mapped[bool] = mapped_column(default=False)
    is_premium: Mapped[bool] = mapped_column(default=False)

    @property
    def full_name(self) -> str:
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or f"Unknown[ID {self.id}]"

    @property
    def url(self) -> str:
        return create_tg_link("user", id=self.id)

    def mention_markdown(self, name: str | None = None) -> str:
        if name is None:
            name = self.full_name
        return markdown.link(name, self.url)

    def mention_html(self, name: str | None = None) -> str:
        if name is None:
            name = self.full_name
        return markdown.hlink(name, self.url)

    @property
    def link(self):
        if self.username:
            return markdown.hlink(self.full_name, f"https://t.me/{self.username}")
        return self.mention_html()
