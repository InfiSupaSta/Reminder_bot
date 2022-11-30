import sqlalchemy.orm
from backend.database.session import session

from backend.logger.create_logger import Logger

logger = Logger('api_logger').create_logger()


# TODO: implement task repository
class TaskRepository:

    def __init__(self, _session=session):
        self.session: sqlalchemy.orm.Session = _session
        self.logger = logger

    def create_task(self, user_telegram_id: int, description: str):
        ...

    def delete_task(self, task_id: int):
        ...

    def _analyze_task_description(self, task_description: str):
        ...

