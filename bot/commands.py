from typing import List

from aiogram import types, dispatcher

bot_commands = [
    types.BotCommand("start", "Some intro information :)"),
    types.BotCommand("help", "How to start"),
    types.BotCommand("register", "First step to interact with bot"),
    types.BotCommand("tasks", "Get list of your tasks"),
    types.BotCommand("goodbye", "Delete all data of you from database"),
    types.BotCommand("am_i_still_registered", "Check if your data still in database"),
]


async def set_bot_commands(dp: dispatcher.Dispatcher, commands: List[types.BotCommand]):
    await dp.bot.set_my_commands(commands)
