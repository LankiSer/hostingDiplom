from fastapi import APIRouter, Depends, Header, HTTPException

from src.schemas.platform import (
    PlatformLoginRequest,
    PlatformRegisterRequest,
    PlatformSessionResponse,
    PlatformSettingsResponse,
    PlatformSettingsUpdateRequest,
    TeamCallCreateRequest,
    TeamCallLivekitConnectionResponse,
    TeamCallMessageRequest,
    TeamCallParticipantsResponse,
    TeamInviteRequest,
    TeamMemberUpdateRequest,
)
from src.core.rbac import CurrentUser, require_permission
from src.services.service import GatewayService

router = APIRouter(prefix="/api/v1/platform")
service = GatewayService()


@router.post("/login", response_model=PlatformSessionResponse)
def login(payload: PlatformLoginRequest) -> PlatformSessionResponse:
    try:
        session = service.login(
            email=payload.email,
            accept_policy=payload.accept_policy,
            accept_personal_data=payload.accept_personal_data,
            password=payload.password,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return PlatformSessionResponse(**session)


@router.get("/session", response_model=PlatformSessionResponse)
def get_session(
    x_platform_email: str = Header(default=""),
) -> PlatformSessionResponse:
    try:
        session = service.session_for_email(email=x_platform_email)
    except ValueError as error:
        raise HTTPException(status_code=401, detail=str(error)) from error
    return PlatformSessionResponse(**session)


@router.get("/invite/accept", response_model=PlatformSessionResponse)
def accept_invite(token: str = "") -> PlatformSessionResponse:
    try:
        session = service.accept_team_invite(token=token)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return PlatformSessionResponse(**session)


@router.post("/register", response_model=PlatformSessionResponse)
def register(payload: PlatformRegisterRequest) -> PlatformSessionResponse:
    try:
        session = service.register(
            display_name=payload.display_name,
            email=payload.email,
            password=payload.password,
            workspace_name=payload.workspace_name,
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
    return service.get_team_overview()


@router.get("/team/overview")
def team_overview() -> dict[str, object]:
    return service.get_team_overview()


@router.post("/team/invite", status_code=201)
def invite_team_member(
    payload: TeamInviteRequest,
    actor: CurrentUser = Depends(require_permission("team:write")),
) -> dict[str, object]:
    try:
        return service.invite_team_member(payload.email, payload.role, actor=actor)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.put("/team/members/{member_id}")
def update_team_member(
    member_id: str,
    payload: TeamMemberUpdateRequest,
    actor: CurrentUser = Depends(require_permission("team:write")),
) -> dict[str, object]:
    try:
        return service.update_team_member(member_id, role=payload.role, status=payload.status, actor=actor)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.post("/team/members/{member_id}/resend-invite")
def resend_team_invite(
    member_id: str,
    actor: CurrentUser = Depends(require_permission("team:write")),
) -> dict[str, object]:
    try:
        return service.resend_team_invite(member_id, actor=actor)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.post("/team/members/{member_id}/cancel-invite")
def cancel_team_invite(
    member_id: str,
    actor: CurrentUser = Depends(require_permission("team:write")),
) -> dict[str, object]:
    try:
        return service.cancel_team_invite(member_id, actor=actor)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.delete("/team/members/{member_id}")
def delete_team_member(
    member_id: str,
    actor: CurrentUser = Depends(require_permission("team:write")),
) -> dict[str, object]:
    try:
        return service.delete_team_member(member_id, actor=actor)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.get("/team/audit")
def team_audit(
    limit: int = 80,
    actor: CurrentUser = Depends(require_permission("audit:read")),
) -> dict[str, object]:
    return service.list_audit(limit=limit)


@router.get("/audit")
def audit(
    limit: int = 80,
    resource_type: str = "",
    actor: CurrentUser = Depends(require_permission("audit:read")),
) -> dict[str, object]:
    return service.list_audit(limit=limit, resource_type=resource_type)


@router.get("/team/calls/active")
def active_call(
    actor: CurrentUser = Depends(require_permission("calls:read")),
) -> dict[str, object] | None:
    return service.get_active_call_session()


@router.post("/team/calls", status_code=201)
def create_call(
    payload: TeamCallCreateRequest,
    actor: CurrentUser = Depends(require_permission("calls:write")),
) -> dict[str, object]:
    return service.create_call_session(payload.title, actor=actor)


@router.get("/team/calls/{session_id}")
def get_call(
    session_id: str,
    actor: CurrentUser = Depends(require_permission("calls:read")),
) -> dict[str, object]:
    try:
        return service.get_call_session(session_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.post("/team/calls/{session_id}/end")
def end_call(
    session_id: str,
    actor: CurrentUser = Depends(require_permission("calls:write")),
) -> dict[str, object]:
    try:
        return service.end_call_session(session_id, actor=actor)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.post("/team/calls/{session_id}/messages", status_code=201)
def add_call_message(
    session_id: str,
    payload: TeamCallMessageRequest,
    actor: CurrentUser = Depends(require_permission("calls:write")),
) -> dict[str, object]:
    try:
        return service.add_call_message(session_id, payload.body, payload.kind, actor=actor)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.get("/team/calls/{session_id}/livekit", response_model=TeamCallLivekitConnectionResponse)
def get_call_livekit(
    session_id: str,
    actor: CurrentUser = Depends(require_permission("calls:read")),
) -> TeamCallLivekitConnectionResponse:
    try:
        return TeamCallLivekitConnectionResponse(**service.get_livekit_connection(session_id, actor=actor))
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.get("/team/calls/{session_id}/participants", response_model=TeamCallParticipantsResponse)
def get_call_participants(
    session_id: str,
    actor: CurrentUser = Depends(require_permission("calls:read")),
) -> TeamCallParticipantsResponse:
    """Get list of participants in a call room."""
    from src.api.call_websocket import room_manager
    
    if session_id not in room_manager.participants:
        return TeamCallParticipantsResponse(session_id=session_id, participants=[])
    
    participants = [
        TeamCallParticipantInfo(**p.model_dump())
        for p in room_manager.participants[session_id].values()
    ]
    return TeamCallParticipantsResponse(session_id=session_id, participants=participants)


@router.post("/team/calls/{session_id}/participants/{identity}/update")
def update_participant_status(
    session_id: str,
    identity: str,
    payload: dict,
    actor: CurrentUser = Depends(require_permission("calls:write")),
) -> dict[str, object]:
    """Update participant status (camera, mic, screen)."""
    from src.api.call_websocket import room_manager
    
    if session_id not in room_manager.participants:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if identity not in room_manager.participants[session_id]:
        raise HTTPException(status_code=404, detail="Participant not found")
    
    participant = room_manager.participants[session_id][identity]
    participant.is_camera_on = payload.get("camera", participant.is_camera_on)
    participant.is_mic_on = payload.get("mic", participant.is_mic_on)
    participant.is_screen_sharing = payload.get("screen", participant.is_screen_sharing)
    
    return {"status": "updated", "participant": participant.model_dump()}


@router.post("/team/calls/{session_id}/participants/{identity}/kick")
def kick_participant(
    session_id: str,
    identity: str,
    actor: CurrentUser = Depends(require_permission("calls:write")),
) -> dict[str, object]:
    """Kick participant from call room (admin only)."""
    from src.api.call_websocket import room_manager
    
    if session_id not in room_manager.rooms:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if identity not in room_manager.rooms[session_id]:
        raise HTTPException(status_code=404, detail="Participant not found")
    
    # Close websocket connection
    try:
        room_manager.rooms[session_id][identity].close(code=4004, reason="Kicked by admin")
    except Exception:
        pass
    
    room_manager.remove_participant(session_id, identity)
    
    return {"status": "kicked", "participant_identity": identity}


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
def update_settings(
    payload: PlatformSettingsUpdateRequest,
    actor: CurrentUser = Depends(require_permission("settings:write")),
) -> PlatformSettingsResponse:
    return PlatformSettingsResponse(**service.update_settings(payload.model_dump(), actor=actor))


@router.get("/documents")
def documents() -> dict[str, object]:
    return service.get_documents()
