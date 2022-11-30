from fastapi import APIRouter

from backend.api.user.schemas import UserSchema
from backend.api.tasks.schemas import TaskSchema
from backend.api.tasks.task_crud_repository import TaskRepository

tasks_router = APIRouter(
    prefix='/api/v1/tasks',
    tags=['task']
)


# TODO: implement task endpoint logic
@tasks_router.post("/create")
async def root(task: TaskSchema):
    ...


@tasks_router.post("/update")
async def root(task: TaskSchema):
    ...


@tasks_router.post("/delete")
async def root(task: TaskSchema):
    ...


@tasks_router.post("/retrieve")
async def root(task: TaskSchema):
    ...
