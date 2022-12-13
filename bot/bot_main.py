import asyncio.tasks

import aiogram
from aiogram import types
from aiogram.utils import executor

from bot_init import dp
from api_related_things.api_request import ApiRequest
from api_related_things.api_methods import ApiMethod
from api_related_things.api_endpoints import ApiEndpoint
from api_related_things.api_tags import Tag
from task_coroutine import TaskTextAnalyze, create_user_task

TASK_PREFIX = 'remind'


@dp.message_handler(commands=['start'])
async def get_start_command(message: types.Message):
    greetings_message = 'Hello from Reminder BOT! Please use next commands to interact with me:\n' \
                        '/help - information about first steps\n' \
                        '/register - required to start interacting with bot\n' \
                        '... or just type command like > REMIND ... TASK ... < if you are already familiar with ' \
                        'bot syntax :)'
    return await message.answer(greetings_message)


@dp.message_handler(commands=['help'])
async def get_help_command(message: types.Message):
    info_message = 'To start interacting with bot first of all you need to register by using /register command.' \
                   'This will give opportunity for creating tasks personally for you. \n' \
                   'After that you can add tasks for reminding according to this pattern: \n ' \
                   'REMIND [date, day, in/every ** minutes/hours] TASK [task_description]'
    return await message.answer(info_message)


@dp.message_handler(commands=['register'])
async def register_user(message: types.Message):
    message_user_id = message.from_user.id
    request_data = {
        'telegram_id': message_user_id
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


tasks = []


@dp.message_handler(commands=['am_i_still_registered'])
async def check_user_still_registered(message: types.Message):
    request_data = {
        'telegram_id': message.from_user.id
    }
    request = ApiRequest(
        url=ApiEndpoint.EXISTS_USER,
        tag=Tag.USER,
        method=ApiMethod.GET,
        **request_data
    )
    response = await request.send()
    return await message.answer(response)


# TODO подумать как хранить таски
@dp.message_handler(commands=['delete_task'])
async def delete_task(message: types.Message):
    global tasks
    try:
        tasks[0].cancel()
        info_message = f'Task {tasks[0].get_name()} cancelled: {tasks[0].cancel()} {tasks[0].cancelled()}, stack: {tasks[0].get_stack()}' \
                       f'\nstate {tasks[0]._state}'
        tasks.pop(0)
    except Exception as e:
        info_message = str(e)

    return await message.answer(info_message)


@dp.message_handler()
async def catch_task_or_unrecognized_command(message: types.Message):
    if message.text.lower().startswith(TASK_PREFIX):

        task_data = TaskTextAnalyze(user_message=message.text).approximate_methods_sequence_to_task_analyze()

        # TODO убрать этот срам
        global tasks

        task_data.update({'user_id': message.from_user.id})
        request = ApiRequest(
            url=ApiEndpoint.CREATE_TASK,
            tag=Tag.TASK,
            method=ApiMethod.POST,
            **task_data
        )
        response = await request.send()
        await message.answer(response)
        # TODO подумать как останавливать запущенные корутины с while true

        await create_user_task(**task_data, message=message, tasks_container=tasks)

    else:
        await message.answer('Unrecognized command, use /help  or side menu for info.')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
