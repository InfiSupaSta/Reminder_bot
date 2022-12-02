from backend.database.engine import engine
from backend.database.base import Base
from backend.logger.create_logger import Logger

logger = Logger(logger_name='database_logger').create_logger()


def create_metadata_tables() -> None:
    try:
        Base.metadata.create_all(engine)
        logger.error(f'Engine: %s', engine)
    except Exception as exception:
        message = f'Raised unexpected exception during the ' \
                  f'tables creation. Detail: {exception}'
        logger.error(message)
