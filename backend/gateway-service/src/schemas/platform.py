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
    permissions: list[str] = []
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


class TeamInviteRequest(BaseModel):
    email: str
    role: str = "ops"


class TeamMemberUpdateRequest(BaseModel):
    role: str | None = None
    status: str | None = None


class TeamCallCreateRequest(BaseModel):
    title: str = "Обсуждение проекта"


class TeamCallMessageRequest(BaseModel):
    body: str
    kind: str = "chat"


class TeamCallLivekitConnectionResponse(BaseModel):
    identity: str
    name: str
    room: str
    token: str
    url: str
    stun_urls: list[str] = []
    turn_url: str | None = None
    turn_username: str | None = None
    turn_password: str | None = None


class TeamCallParticipantInfo(BaseModel):
    identity: str
    name: str
    email: str
    is_camera_on: bool = False
    is_mic_on: bool = True
    is_screen_sharing: bool = False


class TeamCallParticipantsResponse(BaseModel):
    session_id: str
    participants: list[TeamCallParticipantInfo] = []
