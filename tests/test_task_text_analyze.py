import unittest
import sys
import pathlib

sys.path.append(
    pathlib.Path(__file__).parent.parent.as_posix()
)

from bot.task_message_analyze.task_text_analyze import TaskTextAnalyze
from bot.task_message_analyze.exceptions import IncorrectUserMessageException
from bot.task_message_analyze.patterns import EnumPattern


class TestTextAnalyze(unittest.TestCase):
    def setUp(self) -> None:
        self.incorrect_message = 'remind every 10 seconds tas eat something'  # missing 'k' after 'tas'

        self.correct_in_pattern = 'Remind in 2.5 hours task something cool'
        self.correct_messages = {
            'in_pattern': 'Remind in 2.5 hours task something cool',
            'every_pattern': 'Remind every 5 secs task do not be lazy',
            'tomorrow_pattern': 'Remind tomorrow 23:59 task waiting for next day',
            'datetime_pattern': 'Remind 1.1.2023 23:59 task eat some spicy food',
            'daymonthtime_pattern': 'Remind 31 december 23:59 task do some workout'
        }

    def test_incorrect_message(self):
        analyze_instance = TaskTextAnalyze(user_message=self.incorrect_message)
        self.assertFalse(
            analyze_instance.check_user_message_is_correct()
        )
        with self.assertRaises(IncorrectUserMessageException):
            analyze_instance.analyze()

    def test_correct_message_with_in_pattern(self):
        analyze_instance = TaskTextAnalyze(user_message=self.correct_in_pattern)
        analyze_instance.analyze()
        self.assertEqual(
            analyze_instance.get_message_pattern(),
            EnumPattern.IN
        )


if __name__ == '__main__':
    unittest.main()
