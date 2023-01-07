from aiogram.dispatcher.filters.state import State, StatesGroup


class OffsetState(StatesGroup):
    offset = State()


class TimeOffsetValidator:
    OFFSET_RANGE = range(-12, 15)

    def __init__(self, *, offset: str):
        self.offset = offset

    def is_valid(self):
        try:
            return self.OFFSET_RANGE[0] <= float(self.offset) <= self.OFFSET_RANGE[-1]
        except ValueError:
            return False
