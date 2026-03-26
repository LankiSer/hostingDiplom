from fastapi import APIRouter

from src.core.config import get_settings
from src.schemas.contracts import (
    DomainAssignmentRequest,
    DomainAssignmentResponse,
    SslStatusResponse,
    WildcardResponse,
)
from src.services.service import DomainService

router = APIRouter()
settings = get_settings()
service = DomainService()


@router.get("/health")
def health() -> dict[str, str]:
    return {"service": settings.service_name, "status": "ok"}


@router.get("/api/v1/info")
def info() -> dict[str, list[str] | str]:
    return {"name": settings.service_name, "capabilities": settings.capabilities}


@router.post("/api/v1/domains/assign", response_model=DomainAssignmentResponse)
def assign_domain(payload: DomainAssignmentRequest) -> DomainAssignmentResponse:
    return DomainAssignmentResponse(**service.assign_domain(payload))


@router.get("/api/v1/domains/{service_name}/ssl", response_model=SslStatusResponse)
def get_ssl_status(service_name: str) -> SslStatusResponse:
    return SslStatusResponse(**service.get_ssl_status(service_name))


@router.get("/api/v1/domains/wildcard", response_model=WildcardResponse)
def get_wildcard() -> WildcardResponse:
    return WildcardResponse(**service.get_wildcard())
