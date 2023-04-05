import http
import typing
import logging

from api_related_info.api_request import ApiRequest
from api_related_info.api_methods import ApiMethod
from api_related_info.api_endpoints import ApiEndpoint
from api_related_info.api_tags import Tag

logger = logging.getLogger(__file__)


async def check_user_registered(
        *,
        user_id: int,
        status_code_only: bool = False
) -> typing.Union[typing.Tuple[int, str], bool]:
    """
    Check if user exists in database.
    Returns tuple with status code and response based on status code.
    Currently, two responses can be received:\n\n

        (200, 'Yes, you are registered.')  # if user registered\n
        (401, 'Nope, you are not registered.')  # otherwise

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

    if status_code_only:
        return status == http.HTTPStatus.OK

    if status == 200:
        return 200, 'Yes, you are registered.'
    return 401, 'Nope, you are not registered.'
