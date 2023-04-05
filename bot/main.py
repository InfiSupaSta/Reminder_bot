import asyncio
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
    BASE_DIR,
)
from keyboards.tasks_keyboard import InlineTaskKeyboard
from on_startup import on_startup
from services.handle_user_input.message_handler import HandleUserMessage
from states.helper import Helper
from states.offset_state import OffsetState, TimeOffsetValidator
from user_tasks_container.base_container import BaseTasksContainer
from user_tasks_container.tasks_container import UserTasksContainer
from utils.check_user_registered import check_user_registered
from utils.redis_helper.core import RedisHelper

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

tasks_container = UserTasksContainer()


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
    info_message = 'To start interacting with bot first of all you need to register by using /register command. ' \
                   'This will give opportunity for creating tasks personally for you.\n\n' \
                   'Next step is setting up your timezone offset by using /set_user_time_offset command.\n\n' \
                   'After that you can add tasks for reminding according to this pattern:\n' \
                   'REMIND [date, day, in/every ** minutes/hours] TASK [task_description]\n\n' \
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
async def get_tasks_command(message: types.Message, tasks: BaseTasksContainer = tasks_container):
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

    response_message = 'Here is your tasks! You can click on task to delete it.'
    await message.reply(text=response_message, reply_markup=keyboard.get_keyboard())


@dp.callback_query_handler(lambda callback: callback.data.startswith(CALLBACK_DELETE_TASK_PREFIX))
async def delete_task_callback(callback: types.CallbackQuery, tasks: UserTasksContainer = tasks_container):
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
        logger.error(f'Raised during task deletion by user {callback.message.from_user.id} request :: {str(exception)}')
        await callback.message.answer('Something going wrong.')


@dp.message_handler(state='*')
async def handle_user_message(message: types.Message,
                              state: FSMContext,
                              tasks_container: UserTasksContainer = tasks_container):
    """
    Main function to handle user messages that do not match commands(except /cancel,
    that will work only of FSM state is not None and user want to abandon current action).
    """

    message_handler = HandleUserMessage(message, state)

    if await message_handler.get_current_fsm_state() is not None:
        return await message_handler.handle_state()

    if not message_handler.check_if_input_is_task():
        error_message = 'Unrecognized command, use /help  or side menu for info.'
        return await message.answer(error_message)

    if not await check_user_registered(user_id=message.from_user.id, status_code_only=True):
        error_message = 'Please register (/register command) before any actions with task creating.'
        return await message.answer(error_message)

    return await message_handler.handle_task(storage=tasks_container)


async def main():
    await on_startup(dp)
    await dp.start_polling()


# TODO добавить функционал для воссоздания существующих
#  задач в бд в случае непредвиденной остановки работы и перезапуска сервиса

if __name__ == '__main__':
    asyncio.run(
        main()
    )
