import asyncio
import io
import os
import zipfile

from aiogram import Bot, types
from loguru import logger

from src.config import Settings


def get_archive(username: str):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zip_file:
        for root, dirs, files in os.walk("."):
            for file in files:
                zip_file.write(os.path.join(root, file))
    buffer.seek(0)
    document = types.BufferedInputFile(buffer.getvalue(), filename=f"{username}.zip")
    return document


async def send_start_info(settings: Settings, bot: Bot, only_text: bool = True):
    if not settings.bot.admins:
        return
    admin_id = next(iter(settings.bot.admins))
    username = (await bot.me()).username
    info_text = f"Bot @{username} started"
    logger.warning(info_text)
    if only_text:
        await bot.send_message(admin_id, info_text)
        return
    document = await asyncio.to_thread(get_archive, username or "unknown")
    await bot.send_document(
        admin_id,
        document,
        caption=info_text,
    )
