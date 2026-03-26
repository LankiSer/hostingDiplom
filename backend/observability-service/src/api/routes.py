from fastapi import APIRouter

from src.core.config import get_settings
from src.schemas.contracts import EventResponse, LogResponse
from src.services.service import ObservabilityService

router = APIRouter()
settings = get_settings()
service = ObservabilityService()


@router.get("/health")
def health() -> dict[str, str]:
    return {"service": settings.service_name, "status": "ok"}


@router.get("/api/v1/info")
def info() -> dict[str, list[str] | str]:
    return {"name": settings.service_name, "capabilities": settings.capabilities}


@router.get("/api/v1/events")
def list_events() -> dict[str, list[dict[str, str]]]:
    return {"items": service.list_events()}


@router.get("/api/v1/logs/{service_name}", response_model=LogResponse)
def get_logs(service_name: str) -> LogResponse:
    return LogResponse(**service.get_logs(service_name))
