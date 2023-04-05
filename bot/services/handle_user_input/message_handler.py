import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from api_related_info import ApiRequest, ApiEndpoint, Tag, ApiMethod
from global_constants import TASK_PREFIX
from utils.redis_helper.core import RedisHelper
from services.task_message_analyze.exceptions import (
    PatternNotFoundException,
    UnitOfTimeDoesNotFoundException,
    TimeToRemindDoesNotSetException,
    IncorrectUserMessageException
)
from services.task_message_analyze.patterns import EnumPattern
from services.task_message_analyze.task_text_analyze import TaskTextAnalyze
from states.helper import Helper
from user_tasks_container.base_container import BaseTasksContainer

from services.handle_user_input.task_handler import TaskHandler


class HandleUserMessage:
    """
    Class with methods for handling message based on
    FSM state and user input.
    """

    def __init__(
            self,
            message: types.Message,
            state: FSMContext,
            cache_backend=RedisHelper()
    ):
        self.message = message
        self.state = state
        self.cache_backend = cache_backend

    async def get_current_fsm_state(self):
        return await self.state.get_state()

    async def handle_state(self):
        state = await self.get_current_fsm_state()
        if self.message.is_command() and self.message.text == '/cancel':
            return await self.state.set_state(None)

        info_message = f'Probably your input is incorrect or another action is running.\n' \
                       f'State: {Helper.state.get(state)}\n' \
                       f'Possible action: {Helper.action.get(state)}\n' \
                       'Or use /cancel to stop it.'
        return await self.message.answer(info_message)

    def check_if_input_is_task(self) -> bool:
        return self.message.text.lower().startswith(TASK_PREFIX)

    async def check_task_is_valid(self, *, analyze_instance: TaskTextAnalyze):
        try:
            analyze_instance.analyze()
        except (
                PatternNotFoundException,
                UnitOfTimeDoesNotFoundException,
                TimeToRemindDoesNotSetException,
                IncorrectUserMessageException,
        ):
            info_message = 'Can not find pattern for parse your task message.\n' \
                           'Please use /help and /start for more info about tasks structure.'

            return await self.message.answer(info_message)

        return analyze_instance.get_data_for_task()

    async def handle_task(self, *, storage: BaseTasksContainer):

        task_text_analyzer = TaskTextAnalyze(user_message=self.message.text)
        task_data = await self.check_task_is_valid(analyze_instance=task_text_analyzer)

        request_user_id = self.message.from_user.id

        user_key_with_offset = self.cache_backend.make_user_offset_key(user_id=request_user_id)

        if self.cache_backend.check_key_exists(key=user_key_with_offset):
            offset = self.cache_backend.get_key_value(key=user_key_with_offset)
        else:
            request_body = {
                'telegram_id': request_user_id,

                # for getting a response(JSON, or int in this case) from API and
                # not the data based on status code of response. More details in
                # ./api_related_things/api_request.py module
                'pure_api_response': True
            }
            offset_request = ApiRequest(
                url=ApiEndpoint.OFFSET_USER,
                tag=Tag.USER,
                method=ApiMethod.GET,
                **request_body
            )
            offset = await offset_request.send()
            self.cache_backend.set_user_offset(user_id=request_user_id, offset=offset)

        offset = float(offset)

        if task_text_analyzer.pattern not in [EnumPattern.IN, EnumPattern.EVERY]:
            # We dont need to do anything else to remind time
            # if task is regular or user is not manually gave task time.
            # Otherwise user offset must be handled.

            task_data['time_to_remind'] -= offset

        if task_text_analyzer.pattern == EnumPattern.TOMORROW:
            # Due to date calculation for this pattern based on
            # UTC time, we must sure that final time to remind must be
            # formed on user timezone.

            # For example: user offset is +7 hours and his current time is 0:30 of 10 january.
            # User planned to make a task with tomorrow pattern. Obvious it should ends 11 january.
            # But for python program task init time will be 17:30 of 9 january - this is UTC time,
            # so without check below final date will be 10 january - this is wrong.
            if datetime.datetime.now().hour + offset > 24:
                task_data['time_to_remind'] += 24 * 60 * 60

        create_task_request = ApiRequest(
            url=ApiEndpoint.CREATE_TASK,
            tag=Tag.TASK,
            method=ApiMethod.POST,
            user_id=request_user_id,
            **task_data
        )
        response = await create_task_request.send()

        request_user_tasks = storage.get_user_tasks(user_telegram_id=request_user_id)
        if task_data.get('description') in request_user_tasks:
            info_message = f'Task with name "{task_data.get("description")}" already exists.\n' \
                           'Currently, creating tasks with the already existing description not supported.'
            return await self.message.answer(info_message)

        TaskHandler.add_user_task_to_container(
            task_description=task_data.get('description'),
            user_tasks=request_user_tasks
        )

        await self.message.answer(response)
        await TaskHandler.handle_user_task(
            message=self.message,
            **task_data
        )

        self.delete_task_from_storage(request_user_tasks, task_data.get('description'))

    @staticmethod
    def delete_task_from_storage(user_tasks: dict, task_description: str):
        """
        Deletes task from tasks storage by description.
        Currently, tasks stores as {description: task_coro_handler}.
        """

        user_tasks.pop(task_description)
