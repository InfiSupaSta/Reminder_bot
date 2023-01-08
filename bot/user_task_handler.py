import asyncio
from time import time
import datetime
import aiogram


class UserTask:

    @staticmethod
    def delete_user_task_when_done():
        ...

    @staticmethod
    async def add_user_task_to_loop(*,
                                    description: str,
                                    is_regular_remind: bool = False,
                                    time_to_remind: int,
                                    message: aiogram.types.Message,
                                    ) -> None:
        if is_regular_remind:
            while True:
                try:
                    await asyncio.sleep(time_to_remind)
                    await message.answer(description)
                except asyncio.CancelledError:
                    break
        else:
            await message.answer(f'Task created at (UTC): {datetime.datetime.now()}\n'
                                 f'Task ends at (UTC): {datetime.datetime.fromtimestamp(time_to_remind)}\n'
                                 f'Seconds to wait: {time_to_remind - time()}')
            await asyncio.sleep(time_to_remind - time())
            await message.answer(description)

    @staticmethod
    def add_user_task_to_container(*,
                                   task_description: str,
                                   user_tasks: dict
                                   ) -> None:
        user_tasks.update(
            {task_description: asyncio.tasks.current_task()}
        )
