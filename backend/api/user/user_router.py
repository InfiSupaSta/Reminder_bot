from fastapi import APIRouter
from starlette.responses import JSONResponse
from starlette import status

from backend.api.user.user_schemas import UserSchema
from backend.api.user.user_crud_repository import UserRepository

user_router = APIRouter(
    prefix='/api/v1/user',
    tags=['user']
)


@user_router.post("/create")
async def create_user(user: UserSchema):
    return UserRepository().create_user(user.telegram_id)


@user_router.delete("/delete")
async def delete_user(user: UserSchema, request_user_id: int):
    if UserRepository.check_user_from_request_is_account_owner(user_id=user.telegram_id,
                                                               request_user_id=request_user_id):
        return UserRepository().delete_user(user.telegram_id)
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            'status': 'fail',
            'detail': 'Only owner have access to delete info.'
        }
    )


@user_router.patch("/update")
async def update_user(user: UserSchema, time_offset: str):
    return UserRepository().update_user_offset(user_id=user.telegram_id, time_offset=time_offset)


@user_router.get("/me")
async def check_user_exists(user: UserSchema):
    return UserRepository().check_user_exists(telegram_id=user.telegram_id)


@user_router.get("/offset")
async def get_user_offset(user: UserSchema):
    return UserRepository().get_user_offset(user_id=user.telegram_id)
