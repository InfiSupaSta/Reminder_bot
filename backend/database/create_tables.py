from backend.database.engine import engine
from backend.database.base import Base
from backend.database.models.user.model import User
from backend.database.models.task.model import Task
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

# TODO: probably realise database preparations as a class?

# class DatabasePreparation:
#
#     def __init__(self, engine: Engine, database_url: str):
#         self.database_url = database_url
#         self.engine = engine
#
#         self.logger = logger
#
#     def create_metadata_tables(self) -> None:
#         try:
#             Base.metadata.create_all(self.engine)
#         except Exception as exception:
#             message = f'Raised unexpected exception during the ' \
#                       f'tables creation. Detail: {exception.args}'
#             self.logger.error(message)


if __name__ == '__main__':
    create_metadata_tables()
