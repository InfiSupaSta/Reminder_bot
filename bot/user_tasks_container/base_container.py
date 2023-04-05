from abc import ABC, abstractmethod


class BaseTasksContainer(ABC):

    @abstractmethod
    def get_user_tasks(self, *args, **kwargs):
        pass
