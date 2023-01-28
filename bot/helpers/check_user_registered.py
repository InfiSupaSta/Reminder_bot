import typing
import logging
import sys
from pathlib import Path

sys.path.append(
    str(
        Path(__file__).parent.parent
    )
)

from api_related_info.api_request import ApiRequest
from api_related_info.api_methods import ApiMethod
from api_related_info.api_endpoints import ApiEndpoint
from api_related_info.api_tags import Tag

logger = logging.getLogger(__file__)


# TODO подумать насчёт реализации кэша и нужен ли он тут вообще
def cache(function: typing.Callable):
    cached_info_about_registration = {}

    async def wrapper(**kwargs):
        user_id = kwargs['user_id']
        check_user_info_cached = cached_info_about_registration.get(user_id)

        if check_user_info_cached is not None:
            logger.info('cache worked')
            return check_user_info_cached

        response = await function(**kwargs)
        cached_info_about_registration[user_id] = response
        return response

    return wrapper


# @cache
async def check_user_registered(*, user_id: int) -> typing.Tuple[int, str]:
    """
    Check if user exists in database.
    Returns tuple with status code and response based on status code.
    Currently, two responses can be received:\n\n

        (200, 'Yes, you are registered.')  # if user registered\n
        (403, 'Nope, you are not registered.')  # otherwise

    """

    request_data = {
        'telegram_id': user_id
    }
    request = ApiRequest(
        url=ApiEndpoint.EXISTS_USER,
        tag=Tag.USER,
        method=ApiMethod.GET,
        **request_data,
        status_code_only=True
    )

    status = await request.send()
    if status == 200:
        return 200, 'Yes, you are registered.'
    return 403, 'Nope, you are not registered.'
