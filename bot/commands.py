from typing import List

from aiogram import types, dispatcher

bot_commands = [
    types.BotCommand("start", "Some intro information"),
    types.BotCommand("help", "How to start"),
    types.BotCommand("register", "First step to interact with bot"),
    types.BotCommand("set_user_time_offset", "Set offset according to your timezone"),
    types.BotCommand("cancel", "Stop conversation with bot (set state to None)"),
    types.BotCommand("tasks", "Get list of your tasks and opportunity to delete them"),
    types.BotCommand("am_i_still_registered", "Check if your data still in database"),
    types.BotCommand("goodbye", "Delete all data of you from database"),
    types.BotCommand("examples", "Show list of task creation examples"),
]


async def set_bot_commands(dp: dispatcher.Dispatcher, commands: List[types.BotCommand]):
    await dp.bot.set_my_commands(commands)
