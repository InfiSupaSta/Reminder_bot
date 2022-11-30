import os
from pathlib import Path


class PathUtils:

    @staticmethod
    def get_project_root() -> Path:
        current_directory = Path(__file__).parent
        root_directory = current_directory.parent
        return root_directory

    def get_project_logs_path(self):
        path_to_logs = self.get_project_root().joinpath('logs')
        if not os.path.exists(path_to_logs):
            os.mkdir(path_to_logs)
        return path_to_logs

