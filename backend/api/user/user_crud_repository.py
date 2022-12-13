from starlette import status
from starlette.responses import JSONResponse

import sqlalchemy.orm

from backend.database.session import session
from backend.database.models.user_model import User
from backend.database.models.task_model import Task
from backend.logger.create_logger import Logger
from backend.mixins import MakeExceptionMixin

logger = Logger('api_logger').create_logger()


class UserRepository(MakeExceptionMixin):

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
                    'detail': 'user creation failed',
                    'exception': error_message
                }
            )

    def delete_user(self, user_id: int):
        try:
            user = self.session.query(User).where(User.telegram_id == user_id).one()
            self.session.delete(user)
            self.session.commit()

            return JSONResponse(
                status_code=status.HTTP_204_NO_CONTENT,
                content={
                    'status': 'success',
                    'detail': 'user data was successfully deleted',
                    'user': user_id
                }
            )

        except Exception as exception:
            self.session.rollback()
            error_message = self._make_exception_message(exception)
            self.logger.error("Exception raised during user deletion. More info: %s", error_message)

            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    'status': 'fail',
                    'detail': 'user deletion failed',
                    'exception': error_message
                }
            )

    @staticmethod
    def check_user_from_request_is_account_owner(*, user_id: int, request_user_id: int):
        return user_id == request_user_id

    def check_user_exists(self, *, telegram_id: int):
        user = self.session.query(User.telegram_id).where(User.telegram_id == telegram_id).scalar()

        if user:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    'status': 'success',
                    'detail': f'user with id {telegram_id} exists'
                }
            )

        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                'status': 'fail',
                'detail': f'user with id {telegram_id} not registered'
            }
        )
