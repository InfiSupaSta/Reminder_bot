from collections import defaultdict
from typing import Dict

from user_tasks_container.base_container import BaseTasksContainer


class UserTasksContainer(BaseTasksContainer):

    def __init__(self):
        self.users = defaultdict(dict)

    def get_user_tasks(self, *, user_telegram_id: int) -> Dict:
        return self.users[user_telegram_id]

    def __str__(self):
        return str(self.users)
