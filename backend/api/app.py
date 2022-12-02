from fastapi import FastAPI

from backend.database.create_tables import create_metadata_tables
from backend.api.favicon.favicon_router import favicon_router
from backend.api.index.index_router import main_page_router
from backend.api.user.user_router import user_router
from backend.api.tasks.tasks_router import tasks_router
from backend.logger.create_logger import Logger

# setting logging config for whole app
Logger.set_config()

main_api_app = FastAPI()

create_metadata_tables()

# section for adding routers
main_api_app.include_router(favicon_router)
main_api_app.include_router(main_page_router)
main_api_app.include_router(user_router)
main_api_app.include_router(tasks_router)
