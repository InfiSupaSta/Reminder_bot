from fastapi import APIRouter
from starlette.responses import FileResponse

main_page_router = APIRouter()


@main_page_router.get("/")
async def root():
    return {"message": "Hello World"}
