from __future__ import annotations

from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery

from src.apps.bot.callback_data.admin import AdminCallback
from src.apps.bot.callback_data.moderator import ModeratorPermission
from src.config import Settings


class ModeratorPermissionFilter(BaseFilter):
    def __init__(
        self,
        perm: str | None = None,
        # полностью убрать или просто дать предупреждение
        strict: bool = True,
    ):
        self.perm = perm
        self.strict = strict

    async def __call__(
        self,
        call: CallbackQuery,
        settings: Settings,
        callback_data: AdminCallback | None = None,
    ) -> bool | dict:
        perm_str = self.perm
        if not perm_str and callback_data:
            perm_str = callback_data.action

        try:
            perm = ModeratorPermission(perm_str)
        except ValueError:
            return await call.answer("Cant parse permission")

        has_perm = True
        if not settings.bot.have_perm(call.from_user.id, perm):
            if self.strict:
                await call.answer("У вас нет доступа к этой функции")
            has_perm = False

        if self.strict:
            return has_perm
        return {"has_perm": has_perm, "perm": perm}
