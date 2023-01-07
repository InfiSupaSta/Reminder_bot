class TaskException(Exception):
    info_message = None

    def __init__(self, additional_info: str = None):
        self.add_info = additional_info

    def __str__(self):
        return self.info_message + self.add_info if self.add_info else self.info_message


class PatternNotFoundException(TaskException):
    info_message = "User input does not match any pattern for analyze. "

    def __init__(self, additional_info: str = None):
        super().__init__(additional_info)


class UnitOfTimeDoesNotFoundException(Exception):
    info_message = "Unit of time does not found in user input. Cant create task. "

    def __str__(self):
        return self.info_message


class TimeToRemindDoesNotSetException(TaskException):
    info_message = "Time to remind was not set during task analyze. Cant create task. "

    def __init__(self, additional_info: str = None):
        super().__init__(additional_info)
