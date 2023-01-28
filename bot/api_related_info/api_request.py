import logging
import typing

import aiohttp

logger = logging.getLogger(__file__)


class ResponseMessage:
    response = {

        'user': {
            201: 'Registration successful! Now you can interact with bot and add tasks '
                 '(use /help for details).',
            204: 'All info was successfully deleted from database. Hope you come back! :)',
            400: 'Something went wrong:\n'
                 '- for register option: are you sure that you are not already registered?\n'
                 '- for deleting data: more likely data is already deleted, but you can use /am_i_still_registered '
                 'command for check.\n'
                 'If problem still exists, please open issue on github or send ticket to creator by using /ticket '
                 'command.',
            200: 'Success.',
            403: 'Nope, you are not registered.'
        },

        'task': {
            201: 'Task successfully added.',
            204: 'Task successfully deleted.',
            400: 'Something going wrong, please try one more time.',
            422: 'API error: unprocessable entity.'
        }
    }


def catch_exceptions(function: typing.Callable[[typing.Any], typing.Awaitable[typing.Any]]):

    """
    Simple decorator for catching exceptions.
    """

    async def wrapper(*args, **kwargs):
        try:
            return await function(*args, **kwargs)
        except Exception as exception:
            logger.error(f'Exception raised during API Request. Info: {exception.args}')
            message = f'Something going wrong. Please try again later or contact to developer.'
            return message

    return wrapper


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

        If you need a pure response from API and not the response status code based data you must
        add pure_api_response to data and set it to True. It will looks like:

        data = {'param1': 'value1', ..., 'pure_api_response': True}
    """

    def __init__(self, *, url: str, method: str, tag: str, params: dict = None, **data):
        self.url = url
        self.method = method
        self.data = data
        self.tag = tag
        self.params = params

    async def _handle_response(self, response):
        if self.data.get('pure_api_response') is True:
            return await response.text()
        if self.data.get('status_code_only') is True:
            return response.status
        return ResponseMessage.response[self.tag][response.status]

    @catch_exceptions
    async def send(self):
        async with aiohttp.ClientSession() as session:
            request_method = getattr(session, self.method)
            api_response = await request_method(self.url, json=self.data, params=self.params)
            return await self._handle_response(api_response)
