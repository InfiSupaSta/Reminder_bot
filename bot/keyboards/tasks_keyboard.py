from aiogram.types import (InlineKeyboardMarkup,
                           InlineKeyboardButton)

from global_constants import (SEPARATOR,
                              DELETE_TASK_PREFIX)


class InlineTaskKeyboard:

    def __init__(self):
        self.keyboard = InlineKeyboardMarkup()

    def add_buttons_for_every_user_task(self, *, user_tasks: dict, user_telegram_id: int):
        for task in user_tasks:
            callback_data: str = DELETE_TASK_PREFIX + SEPARATOR + task + SEPARATOR + str(user_telegram_id)
            button = InlineKeyboardButton(text=task, callback_data=callback_data)
            self.keyboard.add(button)

    def set_buttons_per_row(self, *, row_width: int):
        self.keyboard.row_width = row_width

    def get_keyboard(self):
        return self.keyboard
