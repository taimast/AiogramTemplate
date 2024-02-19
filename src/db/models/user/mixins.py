from __future__ import annotations

import typing

from sqlalchemy import ForeignKey, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import mapped_column, Mapped, relationship, declared_attr

if typing.TYPE_CHECKING:
    from .user import User


class ReferralMixin:

    @declared_attr
    def referrer_id(cls) -> Mapped[int | None]:
        return mapped_column(ForeignKey(cls.id))

    @declared_attr
    def referrer(cls) -> Mapped[User | None]:
        return relationship(back_populates="referrals", foreign_keys=[cls.referrer_id])

    @declared_attr
    def referrals(cls) -> Mapped[list[User]]:
        return relationship(
            back_populates="referrer",
            foreign_keys=[cls.referrer_id],
            remote_side=cls.id
        )

    def set_referrer(self, referrer: int) -> bool:
        """Set referrer for user"""
        if self.referrer_id or self.id == referrer:
            return False
        else:
            self.referrer_id = referrer
            return True

    @classmethod
    async def all_referrals_count(cls, session: AsyncSession) -> int:
        stmt = select(func.count(cls.id)).where(cls.referrer_id.isnot(None))
        return (await session.execute(stmt)).scalar()


class ConnectMixin:

    @declared_attr
    def connected_user_id(cls) -> Mapped[int | None]:
        return mapped_column(ForeignKey(cls.id))

    @declared_attr
    def connected_user(cls) -> Mapped[User | None]:
        return relationship(foreign_keys=[cls.connected_user_id], remote_side=cls.id, post_update=True)

    async def connect(self, user: User, reverse: bool = True) -> None:
        self.connected_user = user
        if reverse:
            await user.connect(self, reverse=False)

    async def disconnect(self, reverse: bool = True) -> None:
        connected_user = self.connected_user
        self.connected_user = None
        if reverse and connected_user:
            await connected_user.disconnect(reverse=False)
