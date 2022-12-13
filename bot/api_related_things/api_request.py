import aiohttp

from .api_methods import ApiMethod


class ResponseMessage:
    response = {

        'user': {
            201: 'Registration successful! Now you can interact with bot and add tasks '
                 '(use /help for details).',
            204: 'All info was successfully deleted from database. Hope you come back! :)',
            400: 'You requested for register or related to you data deleting command but something went wrong:\n'
                 '- for register option: are you sure that you are not already registered?\n'
                 '- for deleting data: more likely data is already deleted, but you can use /am_i_still_registered '
                 'command for check.\n'
                 'If problem still exists, please open issue on github or send ticket to creator by using /ticket '
                 'command.',
            200: 'Yes, you are still registered!',
            403: 'Nope, you are not registered.'
        },

        'task': {
            201: 'Task successfully added.',
            400: 'Something going wrong, please try one more time.',
            422: 'API error: unprocessable entity.'

        }
    }


class ApiRequest:
    """
    Class for making an API call, available arguments can be found in:
    self.url in ./api_endpoints.ApiEndpoint class
    self.method in ./api_methods.ApiMethod class
    self.tag refers to what part of API you want to interact - available parts in ./api_tags.Tag class
    self.data parameter is body of the request
    self.params is query params

    All arguments except params are required

        # Example of use:

        data = {'param1': 'value1', 'param2': 'value2'}
        request = ApiRequest(
            url=ApiEndpoint.CREATE_USER,
            tag=Tag.USER,
            method=ApiMethod.POST,
            **data
        )
        response = await request.send()

        # which means we make a POST request to part of API that responsible for creating new user
        # with request body that is stored in data variable. response variable represents description
        # accordingly to status code of response. You can see responses in the ResponseMessage class
        # above.
    """

    def __init__(self, *, url: str, method: str, tag: str, params: dict = None, **data):
        self.url = url
        self.method = method
        self.data = data
        self.tag = tag
        self.params = params

    async def _get_request(self, session: aiohttp.ClientSession):
        async with session.get(self.url, json=self.data, params=self.params) as response:
            return ResponseMessage.response[self.tag][response.status]

    async def _post_request(self, session: aiohttp.ClientSession):
        async with session.post(self.url, json=self.data, params=self.params) as response:
            return ResponseMessage.response[self.tag][response.status]

    async def _delete_request(self, session: aiohttp.ClientSession):
        async with session.delete(self.url, json=self.data, params=self.params) as response:
            return ResponseMessage.response[self.tag][response.status]

    async def send(self):
        async with aiohttp.ClientSession() as session:

            if self.method == ApiMethod.GET:
                return await self._get_request(session)

            elif self.method == ApiMethod.POST:
                return await self._post_request(session)

            elif self.method == ApiMethod.DELETE:
                return await self._delete_request(session)
