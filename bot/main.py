import asyncio
import datetime
import http
import logging

from aiogram import types
from aiogram.dispatcher import FSMContext

from api_related_info.api_endpoints import ApiEndpoint
from api_related_info.api_methods import ApiMethod
from api_related_info.api_request import ApiRequest
from api_related_info.api_tags import Tag
from bot_init import dp
from examples.tasks_pattern_examples import TaskPatternExample
from global_constants import (
    CALLBACK_DELETE_TASK_PREFIX,
    SEPARATOR,
    TASK_PREFIX,
    BASE_DIR,
)
from helpers.check_user_registered import check_user_registered
from keyboards.tasks_keyboard import InlineTaskKeyboard
from on_startup import on_startup
from redis_helpers.global_constants import OFFSET_SUFFIX
from redis_helpers.helpers import RedisHelper
from states.helper import Helper
from states.offset_state import OffsetState, TimeOffsetValidator
from task_message_analyze.exceptions import (
    PatternNotFoundException,
    UnitOfTimeDoesNotFoundException,
    TimeToRemindDoesNotSetException,
)
from task_message_analyze.patterns import EnumPattern
from task_message_analyze.task_text_analyze import TaskTextAnalyze
from user_task_handler import UserTask
from user_tasks_container.tasks_container import UserTasksContainer

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] :: %(asctime)s :: %(filename)s(%(lineno)s) :: %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(
            BASE_DIR.joinpath('logs').joinpath('bot_errors.log')
        )
    ]
)
logger = logging.getLogger(__file__)

container = UserTasksContainer()


@dp.message_handler(commands=['start'])
async def get_start_command(message: types.Message):
    greetings_message = 'Hello from Reminder BOT! Please use next commands to interact with me:\n' \
                        '/help - information about first steps\n' \
                        '/tasks - to see your active tasks\n' \
                        '... or just type command like > REMIND ... TASK ... < if you are already familiar with ' \
                        'bot syntax :)'
    return await message.answer(greetings_message)


@dp.message_handler(commands=['help'])
async def get_help_command(message: types.Message):
    info_message = 'To start interacting with bot first of all you need to register by using /register command.' \
                   'This will give opportunity for creating tasks personally for you. \n' \
                   'Next step is setting up your timezone offset by using /set_user_time_offset command.\n' \
                   'After that you can add tasks for reminding according to this pattern: \n ' \
                   'REMIND [date, day, in/every ** minutes/hours] TASK [task_description]\n' \
                   'Examples here: /examples'
    return await message.answer(info_message)


@dp.message_handler(commands=['examples'])
async def get_examples_command(message: types.Message):
    return await message.answer(
        TaskPatternExample.available_patterns()
    )


@dp.message_handler(commands=['cancel'])
async def cancel_command():
    """
    Just reserved namespace 'cancel' for command.
    This command will be used to set current state
    to None and stop conversation with user.
    """
    pass


@dp.message_handler(commands=['register'])
async def register_user(message: types.Message):
    request_data = {
        'telegram_id': message.from_user.id
    }
    request = ApiRequest(
        url=ApiEndpoint.CREATE_USER,
        tag=Tag.USER,
        method=ApiMethod.POST,
        **request_data
    )
    response = await request.send()
    await message.answer(response)


@dp.message_handler(commands=['goodbye'])
async def delete_user(message: types.Message):
    """
    Command to delete all user related info from database.
    """

    message_user_id = message.from_user.id
    request_data = {
        'telegram_id': message_user_id
    }
    params = {
        'request_user_id': message_user_id
    }
    request = ApiRequest(
        url=ApiEndpoint.DELETE_USER,
        tag=Tag.USER,
        method=ApiMethod.DELETE,
        params=params,
        **request_data
    )
    response = await request.send()
    await message.answer(response)


@dp.message_handler(commands=['am_i_still_registered'])
async def check_user_still_registered_command(message: types.Message):
    """
    Check if user is still registered and user related info exists.
    """

    status_code, response = await check_user_registered(
        user_id=message.from_user.id
    )
    return await message.answer(response)


@dp.message_handler(regexp=r'^[+-]{1}[0-9]{1,2}[.,:]?(30|45)?$', state=OffsetState.offset)
async def process_offset(message: types.Message, state: FSMContext):
    """
    This function will handle user input when app state is set to OffsetState:offset.
    All available states can be found in ./states/*_state.py files.
    User input must match the regexp pattern.
    """

    async with state.proxy():
        data_for_validation = TimeOffsetValidator(offset=message.text)
        if data_for_validation.is_valid():
            user_id = message.from_user.id
            offset = message.text

            RedisHelper().set_user_offset(user_id=user_id, offset=offset)

            query_params = {'time_offset': offset}
            body = {'telegram_id': user_id}
            request = ApiRequest(
                url=ApiEndpoint.UPDATE_USER,
                method=ApiMethod.PATCH,
                params=query_params,
                tag=Tag.USER,
                **body
            )
            await request.send()

            msg = f'Offset {offset} successfully set.'
            await message.answer(msg)
        else:
            msg = 'Wrong input, please use command /set_user_time_offset again.\n' \
                  f'More info: {Helper.action.get(await state.get_state())}'
            await message.answer(msg)

    await state.set_state(state=None)


@dp.message_handler(commands=['set_user_time_offset'], state=None)
async def set_user_time_offset(message: types.Message):
    await OffsetState.offset.set()
    info_message = 'Please choose UTC offset for correct task scheduling.\n' \
                   'For example, if you are living in Moscow offset will be +3 hours.\n' \
                   'Input like "+7" or "-9.30" IN RANGE FROM -12 TO +14 expected.'
    await message.answer(info_message)


@dp.message_handler(commands=['tasks'])
async def get_tasks_command(message: types.Message, tasks: UserTasksContainer = container):
    """
    Function to get existing user tasks. It will be formed into inline buttons.
    Pressing onto them will delete this tasks from list.
    """

    user_telegram_id: int = message.from_user.id
    user_tasks: dict = tasks.get_user_tasks(
        user_telegram_id=user_telegram_id
    )

    if not user_tasks:
        info_message = 'You do not have active tasks at this moment. Lets make some!\n' \
                       'Use /help or /start commands for more info.'
        return await message.answer(info_message)

    keyboard = InlineTaskKeyboard()
    keyboard.set_buttons_per_row(row_width=1)
    keyboard.add_buttons_for_every_user_task(
        user_tasks=user_tasks,
        user_telegram_id=user_telegram_id
    )

    await message.reply(text='Here is your tasks!', reply_markup=keyboard.get_keyboard())


@dp.callback_query_handler(lambda callback: callback.data.startswith(CALLBACK_DELETE_TASK_PREFIX))
async def delete_task_callback(callback: types.CallbackQuery, tasks: UserTasksContainer = container):
    """
    Callback that will be called when button in /tasks command is pressed.
    """

    _, task_name, user_id = callback.data.split(SEPARATOR)
    user_tasks = tasks.get_user_tasks(user_telegram_id=int(user_id))
    user_task = user_tasks.get(task_name)

    try:
        user_task.cancel()
        request = ApiRequest(
            url=ApiEndpoint.DELETE_TASK,
            tag=Tag.TASK,
            method=ApiMethod.DELETE,
            params={
                'request_user_id': int(user_id),
                'task_user_id': int(user_id),
                'task_name': task_name
            }
        )
        response = await request.send()
        info_message = f'{response}\nTask description: "{task_name}"'
        await callback.answer(
            text=info_message,
            show_alert=True
        )
        await callback.message.edit_text(
            text=callback.message.text,
            reply_markup=types.InlineKeyboardMarkup()
        )
    except Exception as exception:
        logger.error(f'Raised during task deletion by user request :: {str(exception)}')
        await callback.message.answer(f'Something going wrong.')


@dp.message_handler(state='*')
async def handle_user_message(message: types.Message,
                              state: FSMContext,
                              tasks_container: UserTasksContainer = container):
    """
    Main function to handle user messages that do not match commands(except /cancel,
    that will work only of FSM state is not None and user want to abandon current action).
    """

    current_state = await state.get_state()
    if current_state is not None:
        if message.is_command() and message.text == '/cancel':
            return await state.set_state(None)

        info_message = f'Probably your input is incorrect or another action is running.\n' \
                       f'State: {Helper.state.get(current_state)}\n' \
                       f'Possible action: {Helper.action.get(current_state)}\n' \
                       f'Or use /cancel to stop it.'
        return await message.answer(info_message)

    if message.text.lower().startswith(TASK_PREFIX):

        status_code, _ = await check_user_registered(user_id=message.from_user.id)
        if status_code != http.HTTPStatus.OK:
            error_message = 'Please register (/register command) before any actions with task creating.'
            return await message.answer(error_message)

        try:
            task_text_analyzer = TaskTextAnalyze(user_message=message.text)
            task_text_analyzer.analyze()
            task_data = task_text_analyzer.get_data_for_task()
        except (PatternNotFoundException, UnitOfTimeDoesNotFoundException, TimeToRemindDoesNotSetException):
            info_message = 'Can not find pattern for parse your task message.\n' \
                           'Please use /help and /start for more info about tasks structure.'
            return await message.answer(info_message)

        request_user_id = message.from_user.id

        redis_client = RedisHelper()
        user_key_with_offset = f'{request_user_id}{OFFSET_SUFFIX}'
        if redis_client.check_key_exists(key=user_key_with_offset):
            offset = redis_client.get_key_value(key=user_key_with_offset)
        else:
            request_body = {
                'telegram_id': request_user_id,
                'pure_api_response': True  # for getting a response(JSON, or int in this case) from API and
                # not the data based on status code of response. More details in
                # ./api_related_things/api_request.py module
            }
            offset_request = ApiRequest(
                url=ApiEndpoint.OFFSET_USER,
                tag=Tag.USER,
                method=ApiMethod.GET,
                **request_body
            )
            offset = await offset_request.send()
            redis_client.set_user_offset(user_id=request_user_id, offset=offset)

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

        request_user_tasks = tasks_container.get_user_tasks(user_telegram_id=request_user_id)
        if task_data.get('description') in request_user_tasks:
            info_message = f'Task with name "{task_data.get("description")}" already exists.'
            return await message.answer(info_message)

        UserTask.add_user_task_to_container(
            task_description=task_data.get('description'),
            user_tasks=request_user_tasks
        )

        await message.answer(response)
        await UserTask.handle_user_task(
            message=message,
            **task_data
        )
        request_user_tasks.pop(task_data.get('description'))
    else:
        await message.answer('Unrecognized command, use /help  or side menu for info.')


async def main():
    await on_startup(dp)
    await dp.start_polling()


# TODO добавить функционал для воссоздания существующих
#  задач в бд в случае непредвиденной остановки работы и перезапуска сервиса

if __name__ == '__main__':
    asyncio.run(
        main()
    )
