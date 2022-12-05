import asyncio
import os

from aiogram import Bot, Dispatcher

from commands import bot_commands, set_bot_commands

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

bot = Bot(token=os.environ.get("BOT_TOKEN"))
dp = Dispatcher(bot, loop=loop)
dp.loop.create_task(set_bot_commands(dp, bot_commands))
