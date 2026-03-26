from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.billing_routes import router as billing_router
from src.api.hosting_routes import router as hosting_router
from src.api.platform_routes import router as platform_router
from src.api.routes import router
from src.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.service_name, version=settings.service_version)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=False,
        allow_headers=["*"],
        allow_methods=["*"],
    )
    app.include_router(router)
    app.include_router(platform_router)
    app.include_router(hosting_router)
    app.include_router(billing_router)
    return app
