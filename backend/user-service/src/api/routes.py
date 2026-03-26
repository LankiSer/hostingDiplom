from fastapi import APIRouter

from src.core.config import get_settings
from src.schemas.contracts import UserCreateRequest, UserResponse
from src.services.service import UserService

router = APIRouter()
settings = get_settings()
service = UserService()


@router.get("/health")
def health() -> dict[str, str]:
    return {"service": settings.service_name, "status": "ok"}


@router.get("/api/v1/info")
def info() -> dict[str, list[str] | str]:
    return {"name": settings.service_name, "capabilities": settings.capabilities}


@router.get("/api/v1/users")
def list_users() -> dict[str, list[dict[str, str]]]:
    return {"items": service.list_users()}


@router.post("/api/v1/users", response_model=UserResponse)
def create_user(payload: UserCreateRequest) -> UserResponse:
    return UserResponse(**service.create_user(payload))
