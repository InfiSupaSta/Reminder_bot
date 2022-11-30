import logging
import pathlib

from backend.path_utils import PathUtils

PATH_TO_LOGS: pathlib.Path = PathUtils().get_project_logs_path()


class CustomFileHandler(logging.Handler):

    def __init__(self, filename: str):
        logging.Handler.__init__(self)
        self.filename = PATH_TO_LOGS.joinpath(filename)

    def emit(self, record: logging.LogRecord) -> None:
        log_record_to_string = f"{self.format(record)}"

        with open(self.filename, 'a+') as log_file:
            log_file.write(log_record_to_string)
