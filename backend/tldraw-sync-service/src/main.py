"""tldraw sync service for real-time whiteboard collaboration."""
import os

from fastapi import FastAPI

from src.api import router
from src.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.service_name,
        version=settings.service_version,
        description="Self-hosted tldraw sync backend",
    )
    app.include_router(router)
    return app


app = create_app()


@app.get("/health")
def health() -> dict[str, str]:
    return {"service": "tldraw-sync-service", "status": "ok"}


@app.get("/api/v1/info")
def info() -> dict[str, list[str] | str]:
    return {
        "name": "tldraw-sync-service",
        "capabilities": ["tldraw-sync", "whiteboard-collaboration"],
    }
