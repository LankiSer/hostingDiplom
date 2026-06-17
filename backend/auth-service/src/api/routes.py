from fastapi import APIRouter

from src.core.config import get_settings
from src.schemas.contracts import (
    LoginRequest,
    LoginResponse,
    OrganizationRegistrationRequest,
    OrganizationRegistrationResponse,
    RegisterRequest,
)
from src.services.service import AuthService

router = APIRouter()
settings = get_settings()
service = AuthService()


@router.get("/health")
def health() -> dict[str, str]:
    return {"service": settings.service_name, "status": "ok"}


@router.get("/api/v1/info")
def info() -> dict[str, list[str] | str]:
    return {"name": settings.service_name, "capabilities": settings.capabilities}


@router.post("/api/v1/auth/login", response_model=LoginResponse)
def login(payload: LoginRequest) -> LoginResponse:
    session = service.login(email=payload.email)
    return LoginResponse(email=session.email, token=session.token, type=session.token_type)


@router.post("/api/v1/auth/register", response_model=OrganizationRegistrationResponse)
def register(payload: RegisterRequest) -> OrganizationRegistrationResponse:
    company = payload.company_name or payload.display_name or payload.name or payload.email.split("@")[0]
    return OrganizationRegistrationResponse(
        **service.register_organization(
            OrganizationRegistrationRequest(company_name=company, email=payload.email, inn="")
        )
    )


@router.post(
    "/api/v1/auth/register-organization",
    response_model=OrganizationRegistrationResponse,
)
def register_organization(
    payload: OrganizationRegistrationRequest,
) -> OrganizationRegistrationResponse:
    return OrganizationRegistrationResponse(**service.register_organization(payload))
