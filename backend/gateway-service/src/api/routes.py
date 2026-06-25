from fastapi import APIRouter

from src.core.config import get_settings
from src.services.service import GatewayService

router = APIRouter()
settings = get_settings()
service = GatewayService()


@router.get("/health")
def health() -> dict[str, str]:
    return {"service": settings.service_name, "status": "ok"}


@router.get("/api/v1/info")
def info() -> dict[str, list[str] | str]:
    return {"name": settings.service_name, "capabilities": settings.capabilities}


@router.get("/api/v1/platform/ws/status")
def websocket_status() -> dict[str, object]:
    return {
        "call_signaling": "/api/v1/platform/ws/calls/{session_id}",
        "tldraw_sync": "/api/v1/platform/ws/tldraw/{room_id}",
        "livekit_proxy": "/livekit/",
        "status": "ok",
    }


@router.get("/api/v1/routes")
def routes() -> dict[str, list[dict[str, str]]]:
    return {"items": service.list_routes()}
