import pathlib

from global_constants import BASE_DIR


def ensure_logs_dir_exists(
        logs_folder_name: str = 'logs'
) -> pathlib.Path:
    path_to_logs = pathlib.Path(BASE_DIR).joinpath(logs_folder_name)
    if not path_to_logs.exists():
        path_to_logs.mkdir()
    return path_to_logs
