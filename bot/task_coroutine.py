import re
import asyncio
from decimal import Decimal
from datetime import timedelta
from time import time

import aiogram.types

Loop = asyncio.AbstractEventLoop

REMIND = 'remind'
TASK = 'task'


class Pattern:
    EVERY = r'^remind every \w+'


COMPILED_PATTERN_HASHMAP = {
    'every': re.compile(Pattern.EVERY, re.IGNORECASE)
}


class PatternNotFoundException(Exception):
    info_message = "User input does not match any pattern for analyze."

    def __str__(self):
        return self.info_message


class TaskTextAnalyze:
    required_parts_of_user_input = ['remind', 'task']

    def __init__(self, *, user_message: str):
        self.text = user_message
        self.task_description = None
        self.is_regular_remind = False
        self.time_to_remind = None
        self.pattern = None

    def get_task_time(self):
        when = self._user_message_to_lower_case().split(TASK)[0].removeprefix(REMIND).strip().removeprefix(self.pattern)
        return when.strip()

    def _get_task_description(self) -> str:
        description = self._user_message_to_lower_case().split(TASK)[1]
        return description.strip()

    def _set_description(self) -> None:
        self.task_description = self._get_task_description()

    def check_user_message_is_correct(self) -> bool:
        return all(required_string in self._user_message_to_lower_case()
                   for required_string in self.required_parts_of_user_input)

    def _user_message_to_lower_case(self) -> str:
        return self.text.lower()

    def get_message_pattern(self) -> str:
        for pattern_name, pattern_expression in COMPILED_PATTERN_HASHMAP.items():
            if pattern_expression.match(self.text):
                self.pattern = pattern_name
                return pattern_name

        raise PatternNotFoundException()

    def check_is_task_regular(self):
        if self.pattern == 'every':
            self.is_regular_remind = True

    def get_data_for_task(self):
        data = {
            'description': self.task_description,
            'is_regular_remind': self.is_regular_remind,
            'time_to_remind': self.time_to_remind
        }
        return data

    def _set_task_time(self) -> None:
        amount, unit_of_time = self.get_task_time().split()
        _timedelta = self.get_timedelta(float(Decimal(amount)), unit_of_time)
        if self.is_regular_remind:
            self.time_to_remind = _timedelta
        else:
            self.time_to_remind = time() + _timedelta

    @staticmethod
    def get_timedelta(amount: float, unit_of_time: str) -> int:
        if 'sec' in unit_of_time:
            return timedelta(seconds=amount).seconds
        elif 'min' in unit_of_time:
            return timedelta(minutes=amount).seconds
        elif 'hour' in unit_of_time:
            return timedelta(hours=amount).seconds
        elif 'day' in unit_of_time:
            return timedelta(days=amount).seconds

    def approximate_methods_sequence_to_task_analyze(self):
        self.check_user_message_is_correct()
        self.get_message_pattern()
        self.check_is_task_regular()
        self._set_description()
        self._set_task_time()

        return self.get_data_for_task()


async def create_user_task(*,
                           description: str,
                           is_regular_remind: bool = False,
                           time_to_remind: int,
                           message: aiogram.types.Message,
                           tasks_container: list
                           ) -> None:
    tasks_container.append(asyncio.tasks.current_task())

    if is_regular_remind:
        while True:
            try:
                await asyncio.sleep(time_to_remind)
                await message.answer(description)
            except asyncio.CancelledError:
                break
    else:
        await asyncio.sleep(time_to_remind)
        await message.answer(description)
