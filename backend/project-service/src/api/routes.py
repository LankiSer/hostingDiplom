from fastapi import APIRouter

from src.core.config import get_settings
from src.schemas.contracts import (
    MicroserviceCreateRequest,
    MicroserviceResponse,
    ProjectCreateRequest,
    ProjectResponse,
)
from src.services.service import ProjectService

router = APIRouter()
settings = get_settings()
service = ProjectService()


@router.get("/health")
def health() -> dict[str, str]:
    return {"service": settings.service_name, "status": "ok"}


@router.get("/api/v1/info")
def info() -> dict[str, list[str] | str]:
    return {"name": settings.service_name, "capabilities": settings.capabilities}


@router.get("/api/v1/projects")
def list_projects() -> dict[str, list[dict[str, str]]]:
    return {"items": service.list_projects()}


@router.post("/api/v1/projects", response_model=ProjectResponse)
def create_project(payload: ProjectCreateRequest) -> ProjectResponse:
    return ProjectResponse(**service.create_project(payload))


@router.post("/api/v1/microservices", response_model=MicroserviceResponse)
def create_microservice(payload: MicroserviceCreateRequest) -> MicroserviceResponse:
    return MicroserviceResponse(**service.create_microservice(payload))
