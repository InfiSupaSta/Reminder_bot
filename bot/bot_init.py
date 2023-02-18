import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

storage = MemoryStorage()

if not os.getenv('BOT_TOKEN'):
    raise ValueError(
        "BOT_TOKEN must be set in .env file before starting bot."
    )

bot = Bot(token=os.environ.get("BOT_TOKEN"))
dp = Dispatcher(bot, storage=storage)
