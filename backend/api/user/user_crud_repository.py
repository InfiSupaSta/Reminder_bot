from typing import Union, Tuple, Any

from starlette import status
from starlette.responses import JSONResponse

import sqlalchemy.orm

from backend.database.session import session
from backend.database.models.user_model import User
from backend.logger.create_logger import Logger

logger = Logger('api_logger').create_logger()


class UserRepository:

    def __init__(self, _session=session):
        self.session: sqlalchemy.orm.Session = _session
        self.logger = logger

    def create_user(self, user_telegram_id: int):
        try:
            new_user = User(telegram_id=user_telegram_id)
            self.session.add(new_user)
            self.session.commit()
            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={
                    'status': 'success',
                    'detail': 'new user created',
                    'user': user_telegram_id
                }
            )

        except Exception as exception:
            self.session.rollback()
            error_message = self._make_exception_message(exception)
            self.logger.error("Exception raised during user creation. More info: %s", error_message)

            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    'status': 'fail',
                    'detail': error_message
                }
            )

    @staticmethod
    def _make_exception_message(exception: Exception) -> Union[str, Tuple[Any]]:
        try:
            error_message: str = exception.args[0]
            error_detail = error_message.split('DETAIL')[1]
            return error_detail
        except Exception:
            return exception.args
