from datetime import datetime

import sqlalchemy.orm
from sqlalchemy import and_
from starlette import status
from starlette.responses import JSONResponse

from backend.database.models import Task
from backend.database import session
from backend.logger import Logger
from backend.mixins import MakeExceptionMixin

logger = Logger('api_logger').create_logger()


class TaskRepository(MakeExceptionMixin):

    def __init__(self, _session=session):
        self.session: sqlalchemy.orm.Session = _session
        self.logger = logger

    def create_task(self, *,
                    user_telegram_id: int,
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

    def delete_task(self, task_name: str):
        try:
            task_to_delete = self.session.query(Task).where(Task.description == task_name).first()
            self.session.delete(task_to_delete)
            self.session.commit()

            return JSONResponse(
                status_code=status.HTTP_204_NO_CONTENT,
                content={
                    'status': 'success',
                    'detail': f'task {task_name} deleted'
                }
            )

        except Exception as exception:
            self.session.rollback()
            error_message = self._make_exception_message(exception)
            self.logger.error("Exception raised during task deletion. Task id: %s. More info: %s",
                              task_name,
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

    def finish_user_task(self, telegram_user_id: int, task_description: str):

        task_to_update = self.session.query(Task).where(
            and_(
                Task.user_id == telegram_user_id,
                Task.description == task_description
            )
        ).scalar()

        if not task_to_update:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={'detail': 'task not found'}
            )

        try:
            task_to_update.is_done = True
            self.session.add(task_to_update)
            self.session.commit()
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    'status': 'success',
                    'detail': f'task <{task_description}> of user <{telegram_user_id}> updated'
                }
            )

        except Exception as exception:
            self.session.rollback()
            error_message = self._make_exception_message(exception)
            self.logger.error("Exception raised during task update. User id: %s. More info: %s",
                              telegram_user_id, error_message)

            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    'status': 'fail',
                    'detail': error_message
                }
            )
