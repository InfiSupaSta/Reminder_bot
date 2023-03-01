import unittest
import sys
import pathlib

sys.path.append(
    pathlib.Path(__file__).parent.parent.parent.as_posix()
)

from bot.task_message_analyze.task_text_analyze import TaskTextAnalyze
from bot.task_message_analyze.exceptions import IncorrectUserMessageException
from bot.task_message_analyze.patterns import EnumPattern


class TestTextAnalyze(unittest.TestCase):
    def setUp(self) -> None:
        self.incorrect_message = 'remind every 10 seconds tas eat something'  # missing 'k' after 'tas'

        self.correct_in_pattern = 'Remind in 2.5 hours task something cool'
        self.correct_every_pattern = 'Remind every 5 secs task do not be lazy'
        self.correct_tomorrowtime_pattern = 'Remind tomorrow 23:59 task waiting for next day'
        self.correct_datetime_pattern = 'Remind 1.1.2023 23:59 task eat some spicy food'
        self.correct_daymonthtime_pattern = 'Remind 31 december 23:59 task do some workout'

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

    def test_correct_message_with_every_pattern(self):
        analyze_instance = TaskTextAnalyze(user_message=self.correct_every_pattern)
        analyze_instance.analyze()
        self.assertEqual(
            analyze_instance.get_message_pattern(),
            EnumPattern.EVERY
        )
        self.assertEqual(analyze_instance.is_regular_remind, True)
        self.assertEqual(
            analyze_instance.get_data_for_task(),
            {
                'description': analyze_instance.task_description,
                'is_regular_remind': True,
                'time_to_remind': analyze_instance.time_to_remind,
            }
        )

    def test_correct_message_with_tomorrowtime_pattern(self):
        analyze_instance = TaskTextAnalyze(user_message=self.correct_tomorrowtime_pattern)
        analyze_instance.analyze()
        self.assertEqual(
            analyze_instance.get_message_pattern(),
            EnumPattern.TOMORROW
        )

    def test_correct_message_with_datetime_pattern(self):
        analyze_instance = TaskTextAnalyze(user_message=self.correct_datetime_pattern)
        analyze_instance.analyze()
        self.assertEqual(
            analyze_instance.get_message_pattern(),
            EnumPattern.DATE_TIME
        )

    def test_correct_message_with_daymonthtime_pattern(self):
        analyze_instance = TaskTextAnalyze(user_message=self.correct_daymonthtime_pattern)
        analyze_instance.analyze()
        self.assertEqual(
            analyze_instance.get_message_pattern(),
            EnumPattern.DAY_MONTH_TIME
        )


if __name__ == '__main__':
    unittest.main()
