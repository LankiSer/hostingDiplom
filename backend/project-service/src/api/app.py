from fastapi import FastAPI

from src.api.routes import router
from src.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.service_name, version=settings.service_version)
    app.include_router(router)
    return app
