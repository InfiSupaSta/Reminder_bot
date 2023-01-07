import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from commands import bot_commands, set_bot_commands

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

storage = MemoryStorage()

bot = Bot(token=os.environ.get("BOT_TOKEN"))
dp = Dispatcher(bot, loop=loop, storage=storage)
dp.loop.create_task(set_bot_commands(dp, bot_commands))
