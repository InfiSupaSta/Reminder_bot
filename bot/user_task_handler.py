import asyncio
import datetime
import logging
from time import time

import aiogram

from api_related_info import (
    ApiRequest,
    ApiEndpoint,
    ApiMethod,
    Tag
)

logger = logging.getLogger(__file__)


class UserTask:

    @staticmethod
    async def delete_user_task_when_done(
            *,
            user_id: int,
            task_name: str,
    ) -> None:
        request_for_task_delete = ApiRequest(
            url=ApiEndpoint.DELETE_TASK,
            tag=Tag.TASK,
            method=ApiMethod.DELETE,
            params={
                'request_user_id': user_id,
                'task_user_id': user_id,
                'task_name': task_name,
            },
            status_code_only=True
        )
        response_from_api = asyncio.create_task(
            request_for_task_delete.send()
        )

        is_response_success = False

        while not is_response_success:
            done, pending = await asyncio.wait(
                fs=[
                    response_from_api
                ],
                timeout=.5,
                return_when=asyncio.FIRST_EXCEPTION
            )

            if response_from_api in done:
                is_response_success = True

    @staticmethod
    async def handle_user_task(
            *,
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

        await UserTask.delete_user_task_when_done(
            user_id=message.from_user.id,
            task_name=description
        )

    @staticmethod
    def add_user_task_to_container(
            *,
            task_description: str,
            user_tasks: dict
    ) -> None:
        """
        Adding newly created user task to a container.
        It gives opportunity to handle it in the future -
        cancel after user request, for example.
        """
        user_tasks.update(
            {task_description: asyncio.tasks.current_task()}
        )
