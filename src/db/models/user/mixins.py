from __future__ import annotations

import typing

from sqlalchemy import ForeignKey, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, relationship

if typing.TYPE_CHECKING:
    from .user import User


class ReferralMixin:
    @declared_attr
    def referrer_id(cls) -> Mapped[int | None]:
        return mapped_column(ForeignKey(cls.id))  # type: ignore

    @declared_attr
    def referrer(cls) -> Mapped[User | None]:
        return relationship(
            back_populates="referrals",
            foreign_keys=[cls.referrer_id],  # type: ignore
        )

    @declared_attr
    def referrals(cls) -> Mapped[list[User]]:
        return relationship(
            back_populates="referrer",
            foreign_keys=[cls.referrer_id],  # type: ignore
            remote_side=cls.id,  # type: ignore
        )

    def set_referrer(self, referrer: int) -> bool:
        """Set referrer for user"""
        if self.referrer_id or self.id == referrer:  # type: ignore
            return False
        self.referrer_id = referrer
        return True

    @classmethod
    async def all_referrals_count(cls, session: AsyncSession) -> int:
        stmt = select(func.count(cls.id)).where(cls.referrer_id.isnot(None))  # type: ignore
        return (await session.execute(stmt)).scalar()  # type: ignore


class ConnectMixin:
    @declared_attr
    def connected_user_id(cls) -> Mapped[int | None]:
        return mapped_column(ForeignKey(cls.id))  # type: ignore

    @declared_attr
    def connected_user(cls) -> Mapped[User | None]:
        return relationship(
            foreign_keys=[cls.connected_user_id],  # type: ignore
            remote_side=cls.id,  #  type: ignore
            post_update=True,
        )

    async def connect(self, user: typing.Self, reverse: bool = True) -> None:
        self.connected_user = user
        if reverse:
            await user.connect(self, reverse=False)

    async def disconnect(self, reverse: bool = True) -> None:
        connected_user = self.connected_user
        self.connected_user = None
        if reverse and connected_user:
            await connected_user.disconnect(reverse=False)  # type: ignore
