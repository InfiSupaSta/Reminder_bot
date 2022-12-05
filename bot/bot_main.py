import aiogram
from aiogram import types
from aiogram.utils import executor

from bot_init import dp
from api_related_things.api_request import ApiRequest
from api_related_things.api_methods import ApiMethod
from api_related_things.api_endpoints import ApiEndpoint
from api_related_things.api_tags import Tag

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


@dp.message_handler()
async def get_start_command(message: types.Message):
    if message.text.lower().startswith(TASK_PREFIX):
        await message.answer('It is task!')
    else:
        await message.answer('Unrecognized command, use /help for info.')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
