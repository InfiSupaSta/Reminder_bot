import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

storage = MemoryStorage()

bot = Bot(token=os.environ.get("BOT_TOKEN"))
dp = Dispatcher(bot, storage=storage)
