from pathlib import Path

from fastapi import APIRouter
from starlette.responses import FileResponse

favicon_router = APIRouter()


@favicon_router.get('/favicon.ico', include_in_schema=False)
async def get_path_to_favicon():
    favicon_path = Path(__file__).parent.joinpath('favicon.ico')
    return FileResponse(favicon_path)
