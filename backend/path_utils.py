from pathlib import Path


class PathUtils:
    logs_folder_name = 'logs'

    @staticmethod
    def get_project_root() -> Path:
        current_directory = Path(__file__).parent
        root_directory = current_directory.parent
        return root_directory

    def get_project_logs_path(self):
        path_to_logs = self.get_project_root().joinpath(self.logs_folder_name)
        if not Path.exists(path_to_logs):
            Path.mkdir(path_to_logs)
        return path_to_logs
