from aiogram.types import BotCommand

bot_commands = [
    BotCommand("start", "Some intro information"),
    BotCommand("help", "How to start"),
    BotCommand("register", "First step to interact with bot"),
    BotCommand("set_user_time_offset", "Set offset according to your timezone"),
    BotCommand("cancel", "Stop conversation with bot (set state to None)"),
    BotCommand("tasks", "Get list of your tasks and opportunity to delete them"),
    BotCommand("am_i_still_registered", "Check if your data still in database"),
    BotCommand("goodbye", "Delete all data of you from database"),
    BotCommand("examples", "Show list of task creation examples"),
]
