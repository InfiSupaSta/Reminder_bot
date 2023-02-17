from backend.database.base import Base
from backend.database.engine import engine
from backend.logger import Logger
from backend.database.models import *

__all__ = [
    'create_metadata_tables',
]

logger = Logger(logger_name='database_logger').create_logger()


def create_metadata_tables() -> None:
    try:

        Base.metadata.create_all(engine)
    except Exception as exception:
        message = f'Raised unexpected exception during the ' \
                  f'tables creation. Detail: {exception}'
        logger.error(message)
