from fastapi import APIRouter

from backend.api.user.user_schemas import UserSchema
from backend.api.tasks.tasks_schemas import TaskSchema
from backend.api.tasks.tasks_crud_repository import TaskRepository

tasks_router = APIRouter(
    prefix='/api/v1/tasks',
    tags=['task']
)


# TODO: implement task endpoint logic
@tasks_router.post("/create")
async def create_task(task: TaskSchema):
    ...


@tasks_router.post("/update")
async def update_task(task: TaskSchema):
    ...


@tasks_router.post("/delete")
async def delet_task(task: TaskSchema):
    ...


@tasks_router.post("/retrieve")
async def retrieve_task(task: TaskSchema):
    ...
