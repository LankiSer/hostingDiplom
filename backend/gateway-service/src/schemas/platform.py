from pydantic import BaseModel


class PlatformLoginRequest(BaseModel):
    email: str
    password: str = ""
    accept_policy: bool = False
    accept_personal_data: bool = False


class PlatformRegisterRequest(BaseModel):
    display_name: str
    email: str
    password: str = ""
    workspace_name: str = ""
    accept_policy: bool
    accept_personal_data: bool


class PlatformSessionResponse(BaseModel):
    companyName: str
    displayName: str
    email: str
    role: str
    token: str


class PlatformSettingsResponse(BaseModel):
    api_host: str
    company_name: str
    contact_email: str
    contact_name: str
    dashboard_host: str
    default_app_domain: str
    support_email: str
    workspace_name: str


class PlatformSettingsUpdateRequest(BaseModel):
    api_host: str
    company_name: str
    contact_email: str
    contact_name: str
    dashboard_host: str
    default_app_domain: str
    support_email: str
    workspace_name: str
