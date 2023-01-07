from collections import defaultdict
from typing import Dict


class UserTasksContainer:

    def __init__(self):
        self.users = defaultdict(dict)

    def get_user_tasks(self, *, user_telegram_id: int) -> Dict:
        return self.users[user_telegram_id]

    def __str__(self):
        return str(self.users)
