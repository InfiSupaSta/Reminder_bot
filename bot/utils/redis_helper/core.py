from typing import Union

from redis import Redis
from utils.redis_helper.constants import OFFSET_SUFFIX, DAY_TTL


class RedisHelper:
    """
    Class for processing user offset.
    Offset storing in key according to pattern <user_id>:offset
    and basically in redis context looks like:
      SETEX <user_id>:offset 86400 <offset_value>

    host parameter of __init__ method is set to 'redis' by default -
    it is name of service with redis from docker-compose.
    """

    def __init__(self, host: str = 'redis'):
        self.client = Redis(host=host)

    def check_key_exists(self, *, key: str) -> int:
        return self.client.exists(key)

    def set_user_offset(self, *, user_id: Union[int, str], offset: str) -> None:
        user_ofsset_key = self.make_user_offset_key(user_id=user_id)
        offset_from_hours_to_seconds = float(offset) * 60 * 60
        self.client.setex(user_ofsset_key, DAY_TTL, offset_from_hours_to_seconds)

    def get_key_value(self, *, key: str) -> bytes:
        return self.client.get(key)

    @staticmethod
    def make_user_offset_key(*, user_id: int, suffix: str = OFFSET_SUFFIX) -> str:
        return f'{user_id}{suffix}'
