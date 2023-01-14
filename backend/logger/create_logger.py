from typing import List

import logging.config

from backend.logger.exceptions import LoggerNotFoundException
from backend.logger.config import config


class Logger:

    def __init__(self, logger_name: str):
        self.logger_name = logger_name

    def create_logger(self) -> logging.getLogger:
        """
        Function to get logger.
        :param logger_name: you can see available loggers in ./logger/config.py.
        :return: logger instance.
        """
        self._check_logger_exists()

        logger = logging.getLogger(self.logger_name)

        return logger

    def _check_logger_exists(self) -> None:
        if self.logger_name not in config['loggers']:
            error_message = f"Undefined logger name: >>> {self.logger_name} <<<. " \
                            f"List of available loggers: {self.get_available_loggers()}"
            raise LoggerNotFoundException(error_message)

    @staticmethod
    def set_config() -> None:
        logging.config.dictConfig(config)

    @staticmethod
    def get_available_loggers() -> List[str]:
        return [logger for logger in config['loggers']]
