import aiohttp

from .api_methods import ApiMethod


# TODO: подумать насчёт разных 4хх ответов для регистрации и удаления юзера
class ResponseMessage:
    response = {
        'user': {
            201: 'Registration successful! Now you can interact with bot and add tasks '
                 '(use /help for details).',
            204: 'All info was successfully deleted from database. Hope you come back! :)',
            400: 'Registration process failed. Probably you are already registered?'
        },
        # TODO: добавить описание ответов для взаимодействия с тасками
        'task': {
            201: '',
            400: ''
        }
    }


class ApiRequest:

    def __init__(self, *, url: str, method: str, tag: str, **data):
        self.url = url
        self.method = method
        self.data = data
        self.tag = tag

    async def _get_request(self, session: aiohttp.ClientSession):
        async with session.get(self.url, json=self.data) as response:
            return ResponseMessage.response[self.tag][response.status]

    async def _post_request(self, session: aiohttp.ClientSession):
        async with session.post(self.url, json=self.data) as response:
            return ResponseMessage.response[self.tag][response.status]

    async def _delete_request(self, session: aiohttp.ClientSession):
        async with session.delete(self.url, json=self.data) as response:
            return ResponseMessage.response[self.tag][response.status]

    async def send(self):
        async with aiohttp.ClientSession() as session:

            if self.method == ApiMethod.GET:
                return await self._get_request(session)

            elif self.method == ApiMethod.POST:
                return await self._post_request(session)

            elif self.method == ApiMethod.DELETE:
                return await self._delete_request(session)
