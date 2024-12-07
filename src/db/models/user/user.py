from __future__ import annotations

import datetime
import typing

from aiogram.utils import markdown as md
from sqlalchemy import Text, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, aliased, mapped_column, relationship

from src.db.models.user.mixins import ReferralMixin

from .base import BaseUser
from .locale import Locale

if typing.TYPE_CHECKING:
    from ..invoice import Invoice
    from .light import LightUser


class User(BaseUser, ReferralMixin):
    __tablename__ = "users"
    language_code: Mapped[Locale] = mapped_column(default=Locale.RUSSIAN)
    invoices: Mapped[list[Invoice]] = relationship(back_populates="user")
    notes: Mapped[str] = mapped_column(Text, default="")

    @classmethod
    async def today_count(cls, session: AsyncSession) -> int:
        result = await session.execute(select(cls).where(cls.created_at >= datetime.date.today()))
        return len(result.all())

    def pretty(self):
        return f"{self.full_name} @{self.username}"

    @classmethod
    async def get_users_with_referral_counts(
        cls,
        session: AsyncSession,
        *expr,
    ) -> typing.Sequence[tuple[User, int]]:
        """
        Асинхронный классовый метод для получения
          списка всех пользователей с количеством их рефералов.
        Возвращает список кортежей (User, referral_count).
        """
        # Создаем псевдоним для таблицы User
        referral_user = aliased(cls)

        # Создаем подзапрос для подсчета рефералов
        referral_count_subquery = (
            select(
                referral_user.referrer_id,
                func.count(referral_user.id).label("referral_count"),
            )
            .group_by(referral_user.referrer_id)
            .subquery()
        )

        # Формируем основной запрос с соединением таблицы пользователей и подзапроса
        stmt = (
            select(
                cls,  # Выбираем все колонки для пользователя
                referral_count_subquery.c.referral_count,
            )
            .where(*expr)
            .outerjoin(referral_count_subquery, referral_count_subquery.c.referrer_id == cls.id)
            .order_by(referral_count_subquery.c.referral_count.desc().nullslast())
        )

        # Выполняем запрос
        result = await session.execute(stmt)
        # Возвращаем результаты запроса
        return result.all()  # type: ignore

    async def self_referrals_count(self, session: AsyncSession) -> int:
        stmt = select(
            func.count(self.id),  # type: ignore
        ).where(
            User.referrer_id == self.id,
        )
        res = await session.execute(stmt)
        return res.scalar() or 0

    def get_light(self) -> LightUser:
        from .light import LightUser

        return LightUser(
            id=self.id,
            username=self.username,
            language_code=self.language_code,
        )

    def add_note(self, username: str, info: str):
        now = datetime.datetime.now()
        pre_info = f"{now.strftime('%Y-%m-%d %H:%M:%S')} @{username}"
        self.notes += f"{md.hbold(pre_info)}:\n{md.hitalic(info)}\n"

    def clear_notes(self):
        self.notes = ""
