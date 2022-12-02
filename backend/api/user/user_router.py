from fastapi import APIRouter

from backend.api.user.user_schemas import UserSchema
from backend.api.user.user_crud_repository import UserRepository

user_router = APIRouter(
    prefix='/api/v1/user',
    tags=['user']
)


@user_router.post("/create")
async def create_user(user: UserSchema):
    return UserRepository().create_user(user.telegram_id)
