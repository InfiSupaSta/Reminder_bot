from typing import List

from aiogram import Dispatcher, types

from commands import bot_commands


async def on_startup(dispatcher: Dispatcher,
                     commands: List[types.BotCommand] = bot_commands):
    await dispatcher.bot.set_my_commands(commands)
