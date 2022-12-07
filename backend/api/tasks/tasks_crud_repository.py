from datetime import datetime, timedelta

import sqlalchemy.orm
from starlette import status
from starlette.responses import JSONResponse

from backend.database.models.task_model import Task
from backend.database.session import session

from backend.logger.create_logger import Logger
from backend.mixins import MakeExceptionMixin

logger = Logger('api_logger').create_logger()


# TODO: implement task repository
class TaskRepository(MakeExceptionMixin):

    def __init__(self, _session=session):
        self.session: sqlalchemy.orm.Session = _session
        self.logger = logger

    def create_task(self, user_telegram_id: int,
                    description: str,
                    time_to_remind: int,
                    is_regular_remind: bool = False):
        try:
            from_epoch_to_datetime = datetime.fromtimestamp(time_to_remind)
            new_task = Task(user_id=user_telegram_id,
                            description=description,
                            time_to_remind=from_epoch_to_datetime,
                            is_regular_remind=is_regular_remind)
            self.session.add(new_task)
            self.session.commit()
            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={
                    'status': 'success',
                    'detail': 'new task created',
                    'task': str(new_task)
                }
            )

        except Exception as exception:
            self.session.rollback()
            error_message = self._make_exception_message(exception)
            self.logger.error("Exception raised during task creation. More info: %s", error_message)

            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    'status': 'fail',
                    'detail': error_message
                }
            )

    def delete_task(self, task_id: int):
        try:
            task_to_delete = self.session.query(Task).get(task_id)
            self.session.delete(task_to_delete)
            self.session.commit()

        except Exception as exception:
            self.session.rollback()
            error_message = self._make_exception_message(exception)
            self.logger.error("Exception raised during task deletion. Task id: %s. More info: %s",
                              task_id,
                              error_message)

            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    'status': 'fail',
                    'detail': error_message
                }
            )

    @staticmethod
    def check_user_is_task_owner(request_user_id: int, task_user_id: int):
        return request_user_id == task_user_id

    def get_user_tasks(self, telegram_user_id: int):
        return self.session.query(Task).where(Task.user_id == telegram_user_id).all()
