from fastapi import APIRouter

from src.core.config import get_settings
from src.schemas.contracts import (
    DeploymentRequest,
    DeploymentResponse,
    RuntimeDetectionRequest,
    RuntimeDetectionResponse,
)
from src.services.service import DeployService

router = APIRouter()
settings = get_settings()
service = DeployService()


@router.get("/health")
def health() -> dict[str, str]:
    return {"service": settings.service_name, "status": "ok"}


@router.get("/api/v1/info")
def info() -> dict[str, list[str] | str]:
    return {"name": settings.service_name, "capabilities": settings.capabilities}


@router.post("/api/v1/deployments", response_model=DeploymentResponse)
def create_deployment(payload: DeploymentRequest) -> DeploymentResponse:
    return DeploymentResponse(**service.create_deployment(payload))


@router.post("/api/v1/deployments/detect-runtime", response_model=RuntimeDetectionResponse)
def detect_runtime(payload: RuntimeDetectionRequest) -> RuntimeDetectionResponse:
    return RuntimeDetectionResponse(**service.detect_runtime(payload))


@router.get("/api/v1/deployments/{deployment_id}", response_model=DeploymentResponse)
def get_deployment(deployment_id: str) -> DeploymentResponse:
    return DeploymentResponse(**service.get_deployment(deployment_id))
