import pathlib

BASE_DIR = pathlib.Path(__file__).parent

TASK_PREFIX = 'remind'
DELETE_TASK_PREFIX = "delete_task"
SEPARATOR = "__"
CALLBACK_DELETE_TASK_PREFIX = DELETE_TASK_PREFIX + SEPARATOR
