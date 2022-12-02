import asyncio
import os

from aiogram import Bot, Dispatcher

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

bot = Bot(token=os.environ.get("BOT_TOKEN"))
dp = Dispatcher(bot, loop=loop)
