from fastapi import APIRouter

main_page_router = APIRouter()


@main_page_router.get("/")
async def root():
    return {"message": "Welcome to page with literally 0 useful info!"}
