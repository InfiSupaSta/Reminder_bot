import logging
from typing import List

from aiogram import Dispatcher, types

from commands import bot_commands
from helpers.create_logs_dir import ensure_logs_dir_exists

logger = logging.getLogger(__file__)


async def on_startup(
        dispatcher: Dispatcher,
        commands: List[types.BotCommand] = bot_commands
) -> None:
    try:
        ensure_logs_dir_exists()
    except Exception:
        import sys
        exc_type, value, exc_tb = sys.exc_info()

        logger.error(f'Cannot create logs dir for bot. {exc_type} :: {value}')
        sys.exit(1)
    await dispatcher.bot.set_my_commands(commands)
