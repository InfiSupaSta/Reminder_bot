import re
from enum import Enum


class EnumPattern(str, Enum):
    IN = 'in'
    EVERY = 'every'
    TOMORROW = 'tomorrow'
    DATE_TIME = 'date_time'
    DAY_MONTH_TIME = 'day_month_time'

    def __str__(self):
        return self


class Pattern:
    EVERY = r'^remind every \w+'
    IN = r'^remind in \w+'
    TOMORROW = r'remind tomorrow [0-9:-]+'
    DATE_TIME = r'remind [0-9.-]+ [0-9:-]+'
    DAY_MONTH_TIME = r'^remind [0-9]{1,2} \w+ [0-9:-]*'


COMPILED_PATTERN_HASHMAP = {
    EnumPattern.EVERY: re.compile(Pattern.EVERY, re.IGNORECASE),
    EnumPattern.IN: re.compile(Pattern.IN, re.IGNORECASE),
    EnumPattern.TOMORROW: re.compile(Pattern.TOMORROW, re.IGNORECASE),
    EnumPattern.DATE_TIME: re.compile(Pattern.DATE_TIME, re.IGNORECASE),
    EnumPattern.DAY_MONTH_TIME: re.compile(Pattern.DAY_MONTH_TIME, re.IGNORECASE)
}
