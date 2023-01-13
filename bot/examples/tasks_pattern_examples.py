class TaskPatternExample:
    examples_hashmap = {
        'EVERY': 'Remind every 5 secs task do not be lazy',
        'DAY_MONTH_TIME': 'Remind 31 december 23:59 task do some workout',
        'DATE_TIME': 'Remind 1.1.2023 23:59 task eat some spicy food',
        'TOMORROW_TIME': 'Remind tomorrow 23:59 task waiting for next day',
        'IN': 'Remind in 2.5 hours task something cool'
    }

    @property
    def available_patterns(self):
        examples = '\n'.join(example for example in self.examples_hashmap.values())
        return examples
