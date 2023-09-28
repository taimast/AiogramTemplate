from aiogram import types
from aiogram.filters import BaseFilter

from ....db.models import User


class IsConnectedFilter(BaseFilter):
    async def __call__(self, update: types.CallbackQuery | types.Message, user: User):
        return user.connected_user_id
