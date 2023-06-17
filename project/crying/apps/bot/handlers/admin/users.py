import json

from aiogram import Router, types
from aiogram.filters import Text
from sqlalchemy.ext.asyncio import AsyncSession

from .....db.models import User

router = Router()


@router.callback_query(Text("export_users"))
async def export_users(call: types.CallbackQuery, session: AsyncSession):
    await call.message.answer(f"Экспорт пользователей...")
    users = await User.all(session)
    users_data = []
    for user in users:
        users_data.append(user.__dict__)
    json_data = json.dumps(users_data, indent=4, ensure_ascii=False, default=str)
    buffer_file = bytes(json_data, encoding="utf-8")
    file = types.BufferedInputFile(buffer_file, filename="users.json")
    await call.message.answer_document(file)