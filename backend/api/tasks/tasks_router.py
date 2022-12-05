from fastapi import APIRouter
from starlette.requests import Request

from backend.api.tasks.tasks_schemas import TaskSchema
from backend.api.tasks.tasks_crud_repository import TaskRepository

tasks_router = APIRouter(
    prefix='/api/v1/tasks',
    tags=['task']
)


# TODO: implement task endpoint logic
@tasks_router.post("/create")
async def create_task(task: TaskSchema):
    return TaskRepository().create_task(user_telegram_id=task.user_id,
                                        description=task.description,
                                        is_regular_remind=task.is_regular_remind)


@tasks_router.delete("/delete")
async def delete_task(request_user_id: int, task_user_id: int):
    if TaskRepository.check_user_is_task_owner(request_user_id, task_user_id):
        return TaskRepository().delete_task(task_id=task_user_id)


@tasks_router.get("/retrieve")
async def retrieve_task(task: TaskSchema):
    return TaskRepository().retrieve_task(user_id=task.user_id, task_id=task.id)
