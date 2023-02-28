import calendar
from decimal import Decimal
from datetime import timedelta
from datetime import datetime
from typing import Union, Dict, Tuple, List
import logging

from .required_task_keywords import TASK, REMIND
from .exceptions import (
    PatternNotFoundException,
    UnitOfTimeDoesNotFoundException,
    TimeToRemindDoesNotSetException,
    IncorrectUserMessageException,
)
from .patterns import COMPILED_PATTERN_HASHMAP, EnumPattern

DEFAULT_DATE_SEPARATORS = (':', '-', '.')
MONTH_MAPPING = {
    month_name.lower(): month_numerical_value
    for month_name, month_numerical_value
    in zip(list(calendar.month_name)[1:], range(1, 13))
}


class TaskTextAnalyze:
    """
        Class for analyzing user input text to create a task.
        User message MUST include "remind" and "task" keywords for successful creating task data.
        self.text - user input message  # (for example "remind every 10 seconds task do not be lazy")
        self.is_regular_remind - if pattern is EnumPattern.EVERY then task description will be announced
                                 every N seconds (for example in 'remind every 5 seconds task ...' N = 5,
                                 in 'remind every 10 hours task ...' N = 10 * 60 * 60 = 36000). Timer starts since
                                 task is created.
        self.time_to_remind - time to task announcement. For regular tasks(pattern=EnumPattern.EVERY) it will be
                              an number N from example below, otherwise it is timestamp from user message datetime info.
        self.pattern - pattern of the user input message. All available patterns can be found in ./patterns.py file.
    """

    required_parts_of_user_input = [REMIND, TASK]

    def __init__(self, *, user_message: str):
        self.text = user_message
        self.task_description = None
        self.is_regular_remind = False
        self.time_to_remind = None
        self.pattern = None

    def get_task_datetime_info(self) -> str:
        task_time, _ = self._user_message_to_lower_case().split(TASK)
        when_with_pattern = task_time.removeprefix(REMIND).strip()
        when_without_pattern = when_with_pattern.removeprefix(self.pattern).strip()
        return when_without_pattern.strip()

    def _get_task_description(self) -> str:
        _, description = self._user_message_to_lower_case().split(TASK)
        return description.strip()

    def _set_description(self) -> None:
        self.task_description = self._get_task_description()

    def check_user_message_is_correct(self) -> bool:
        return all(required_substring in self._user_message_to_lower_case()
                   for required_substring in self.required_parts_of_user_input)

    def _user_message_to_lower_case(self) -> str:
        return self.text.lower()

    def get_message_pattern(self) -> str:
        for pattern_name, pattern_expression in COMPILED_PATTERN_HASHMAP.items():
            if pattern_expression.match(self.text):
                self.pattern = pattern_name
                return pattern_name

        raise PatternNotFoundException()

    def check_is_task_regular(self) -> None:
        if self.pattern == EnumPattern.EVERY:
            self.is_regular_remind = True

    def get_data_for_task(self) -> Dict[str, Union[str, bool, int]]:
        _data = {
            'description': self.task_description,
            'is_regular_remind': self.is_regular_remind,
            'time_to_remind': self.time_to_remind,
        }
        return _data

    @staticmethod
    def _split_string_by_separators(*, _data: str, separators: Tuple[str] = DEFAULT_DATE_SEPARATORS) -> List[str]:
        whitespace = ' '
        for separator in separators:
            _data = _data.replace(separator, whitespace)
        return _data.split()

    def _set_task_time(self) -> None:
        _timedelta = None

        if self.pattern == EnumPattern.EVERY:
            # task will look like
            # 'remind every 5 secs task do not be lazy'
            # without task and pattern it equals to '5 secs'
            amount, unit_of_time = self.get_task_datetime_info().split()
            _timedelta = self.get_timedelta_for_given_unit_of_time(float(Decimal(amount)), unit_of_time)

        elif self.pattern == EnumPattern.DAY_MONTH_TIME:
            # task will look like
            # 'remind 31 december 23:59 task do some workout'
            # without task and pattern it equals to '31 december 23:59'

            # if time was not provided
            if len(self.get_task_datetime_info().split()) == 2:
                day, month = self.get_task_datetime_info().split()
                _time = '00:00'
                hours, minutes = self._split_string_by_separators(_data=_time)
            else:
                day, month, _time = self.get_task_datetime_info().split()
                hours, minutes = self._split_string_by_separators(_data=_time)

            try:
                month = MONTH_MAPPING[month]
                _timedelta = int(datetime(year=datetime.now().year,
                                          month=month,
                                          day=int(day),
                                          hour=int(hours),
                                          minute=int(minutes)).timestamp()
                                 )
            # if month key does not found(user input incorrect)
            except KeyError:
                additional_info = f'User message was: {self.text}'
                raise PatternNotFoundException(additional_info=additional_info) from None

        elif self.pattern == EnumPattern.DATE_TIME:
            # task will look like
            # 'remind 1.1.2023 23:59 task eat some spicy food'
            # without task and pattern it equals to '1.1.2023 23:59'

            _date, _time = self.get_task_datetime_info().split()
            day, month, year = self._split_string_by_separators(_data=_date)
            hours, minutes = self._split_string_by_separators(_data=_time)
            _timedelta = int(datetime(year=int(year),
                                      month=int(month),
                                      day=int(day),
                                      hour=int(hours),
                                      minute=int(minutes)).timestamp()
                             )

        elif self.pattern == EnumPattern.TOMORROW:
            # task will look like
            # 'remind tomorrow 23:59 task do something'
            # without task and pattern it equals to '23:59'

            _time = self.get_task_datetime_info()
            hours, minutes = self._split_string_by_separators(_data=_time)
            _timedelta = int(datetime(year=datetime.now().year,
                                      month=datetime.now().month,
                                      day=datetime.now().day + 1,
                                      hour=int(hours),
                                      minute=int(minutes)).timestamp()
                             )

        elif self.pattern == EnumPattern.IN:
            # task will look like
            # 'remind in 40 minutes task do something again'
            # without task and pattern it equals to '40 minutes'
            _time = self.get_task_datetime_info()
            amount, unit_of_time = _time.split()
            _timedelta = datetime.now().timestamp() + self.get_timedelta_for_given_unit_of_time(amount=float(amount),
                                                                                                unit_of_time=unit_of_time)

        self.time_to_remind = _timedelta
        if self.time_to_remind is None:
            additional_info = f'User message was: {self.text}'
            logging.error(additional_info)
            raise TimeToRemindDoesNotSetException(additional_info=additional_info)

    @staticmethod
    def get_timedelta_for_non_regular_task(time_data: str):
        return time_data.split()

    @staticmethod
    def get_timedelta_for_given_unit_of_time(amount: float, unit_of_time: str) -> int:
        if 'sec' in unit_of_time:
            return timedelta(seconds=amount).seconds
        elif 'min' in unit_of_time:
            return timedelta(minutes=amount).seconds
        elif 'hour' in unit_of_time:
            return timedelta(hours=amount).seconds
        elif 'day' in unit_of_time:
            return timedelta(days=amount).seconds
        else:
            raise UnitOfTimeDoesNotFoundException()

    def analyze(self) -> None:
        if not self.check_user_message_is_correct():
            raise IncorrectUserMessageException()
        self.get_message_pattern()
        self.check_is_task_regular()
        self._set_description()
        self._set_task_time()
