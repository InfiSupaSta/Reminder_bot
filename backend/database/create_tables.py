from backend.database.engine import engine
from backend.database.base import Base
from backend.logger.create_logger import Logger

from backend.database.models.time_offset_model import TimeOffset
from backend.database.models.task_model import Task
from backend.database.models.user_model import User


logger = Logger(logger_name='database_logger').create_logger()


def create_metadata_tables() -> None:
    try:
        Base.metadata.create_all(engine)
    except Exception as exception:
        message = f'Raised unexpected exception during the ' \
                  f'tables creation. Detail: {exception}'
        logger.error(message)
