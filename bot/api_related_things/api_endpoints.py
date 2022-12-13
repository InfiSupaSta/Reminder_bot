import os


class ApiEndpoint:
    CREATE_USER = os.getenv('CREATE_USER_URL')
    DELETE_USER = os.getenv('DELETE_USER_URL')
    EXISTS_USER = os.getenv('EXISTS_USER_URL')

    CREATE_TASK = os.getenv('CREATE_TASK_URL')
    DELETE_TASK = os.getenv('DELETE_TASK_URL')
