from fastapi import APIRouter, HTTPException

from src.schemas.platform import (
    PlatformLoginRequest,
    PlatformRegisterRequest,
    PlatformSessionResponse,
    PlatformSettingsResponse,
    PlatformSettingsUpdateRequest,
)
from src.services.service import GatewayService

router = APIRouter(prefix="/api/v1/platform")
service = GatewayService()


@router.post("/login", response_model=PlatformSessionResponse)
def login(payload: PlatformLoginRequest) -> PlatformSessionResponse:
    return PlatformSessionResponse(**service.login(payload.email, payload.organization))


@router.post("/register", response_model=PlatformSessionResponse)
def register(payload: PlatformRegisterRequest) -> PlatformSessionResponse:
    try:
        session = service.register(
            company_name=payload.company_name,
            contact_name=payload.contact_name,
            email=payload.email,
            inn=payload.inn,
            accept_policy=payload.accept_policy,
            accept_personal_data=payload.accept_personal_data,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return PlatformSessionResponse(**session)


@router.get("/dashboard")
def dashboard() -> dict[str, object]:
    return service.get_dashboard()


@router.get("/projects")
def projects() -> dict[str, object]:
    return service.get_projects()


@router.get("/projects/{project_id}")
def project_details(project_id: str) -> dict[str, object]:
    return service.get_project_details(project_id)


@router.get("/applications")
def applications() -> dict[str, object]:
    return service.get_applications()


@router.get("/applications/{service_id}")
def application_details(service_id: str) -> dict[str, object]:
    return service.get_application_details(service_id)


@router.get("/domains")
def domains() -> dict[str, object]:
    return service.get_domains()


@router.get("/deployments")
def deployments() -> dict[str, object]:
    return service.get_deployments()


@router.get("/billing")
def billing() -> dict[str, object]:
    return service.get_billing()


@router.get("/activity")
def activity() -> dict[str, object]:
    return service.get_activity()


@router.get("/team")
def team() -> dict[str, object]:
    return service.get_team()


@router.get("/access")
def access() -> dict[str, object]:
    return service.get_access()


@router.get("/settings")
def settings() -> dict[str, object]:
    return service.get_settings()


@router.get("/settings/form", response_model=PlatformSettingsResponse)
def settings_form() -> PlatformSettingsResponse:
    return PlatformSettingsResponse(**service.get_settings_form())


@router.put("/settings/form", response_model=PlatformSettingsResponse)
def update_settings(payload: PlatformSettingsUpdateRequest) -> PlatformSettingsResponse:
    return PlatformSettingsResponse(**service.update_settings(payload.model_dump()))


@router.get("/documents")
def documents() -> dict[str, object]:
    return service.get_documents()
