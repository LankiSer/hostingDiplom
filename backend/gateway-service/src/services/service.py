from dataclasses import asdict

from src.core.rbac import CurrentUser
from src.repositories.platform_repository import PlatformRepository
from src.repositories.repository import GatewayRepository


class GatewayService:
    def __init__(
        self,
        repository: GatewayRepository | None = None,
        platform_repository: PlatformRepository | None = None,
    ) -> None:
        self.repository = repository or GatewayRepository()
        self.platform_repository = platform_repository or PlatformRepository()

    def list_routes(self) -> list[dict[str, str]]:
        return [asdict(route) for route in self.repository.list_routes()]

    def login(
        self,
        email: str,
        accept_policy: bool = False,
        accept_personal_data: bool = False,
        password: str = "",
    ) -> dict[str, object]:
        if not accept_policy or not accept_personal_data:
            raise ValueError("Required legal consents were not accepted.")
        if not email.strip():
            raise ValueError("Email is required.")
        return self.platform_repository.login(email=email, password=password)

    def accept_team_invite(self, token: str) -> dict[str, object]:
        if not token.strip():
            raise ValueError("Token is required.")
        return self.platform_repository.accept_team_invite(token=token)

    def session_for_email(self, email: str) -> dict[str, object]:
        if not email.strip():
            raise ValueError("Email is required.")
        return self.platform_repository.session_for_email(email=email)

    def register(
        self,
        display_name: str,
        email: str,
        accept_policy: bool,
        accept_personal_data: bool,
        password: str = "",
        workspace_name: str = "",
    ) -> dict[str, object]:
        if not accept_policy or not accept_personal_data:
            raise ValueError("Required legal consents were not accepted.")
        if not display_name.strip() or not email.strip():
            raise ValueError("Name and email are required.")
        return self.platform_repository.register(
            display_name=display_name,
            email=email,
            password=password,
            workspace_name=workspace_name,
        )

    def get_dashboard(self) -> dict[str, object]:
        return self.platform_repository.dashboard()

    def get_projects(self) -> dict[str, object]:
        return self.platform_repository.projects()

    def get_project_details(self, project_id: str) -> dict[str, object]:
        return self.platform_repository.project_details(project_id)

    def get_applications(self) -> dict[str, object]:
        return self.platform_repository.applications()

    def get_application_details(self, service_id: str) -> dict[str, object]:
        return self.platform_repository.application_details(service_id)

    def get_domains(self) -> dict[str, object]:
        return self.platform_repository.domains()

    def get_deployments(self) -> dict[str, object]:
        return self.platform_repository.deployments()

    def get_billing(self) -> dict[str, object]:
        return self.platform_repository.billing()

    def get_activity(self) -> dict[str, object]:
        return self.platform_repository.activity()

    def get_team_overview(self) -> dict[str, object]:
        return self.platform_repository.team_overview()

    def invite_team_member(self, email: str, role: str, actor: CurrentUser | None = None) -> dict[str, object]:
        return self.platform_repository.invite_team_member(email=email, role=role, actor=actor)

    def update_team_member(
        self,
        member_id: str,
        role: str | None = None,
        status: str | None = None,
        actor: CurrentUser | None = None,
    ) -> dict[str, object]:
        return self.platform_repository.update_team_member(
            member_id=member_id,
            role=role,
            status=status,
            actor=actor,
        )

    def delete_team_member(self, member_id: str, actor: CurrentUser | None = None) -> dict[str, object]:
        return self.platform_repository.delete_team_member(member_id, actor=actor)

    def resend_team_invite(self, member_id: str, actor: CurrentUser | None = None) -> dict[str, object]:
        return self.platform_repository.resend_team_invite(member_id, actor=actor)

    def cancel_team_invite(self, member_id: str, actor: CurrentUser | None = None) -> dict[str, object]:
        return self.platform_repository.cancel_team_invite(member_id, actor=actor)

    def list_audit(self, limit: int = 80, resource_type: str = "") -> dict[str, object]:
        return self.platform_repository.list_audit(limit=limit, resource_type=resource_type)

    def create_call_session(self, title: str, actor: CurrentUser | None = None) -> dict[str, object]:
        return self.platform_repository.create_call_session(title, actor=actor)

    def get_active_call_session(self) -> dict[str, object] | None:
        return self.platform_repository.get_active_call_session()

    def get_call_session(self, session_id: str) -> dict[str, object]:
        return self.platform_repository.get_call_session(session_id)

    def end_call_session(self, session_id: str, actor: CurrentUser | None = None) -> dict[str, object]:
        return self.platform_repository.end_call_session(session_id, actor=actor)

    def add_call_message(
        self,
        session_id: str,
        body: str,
        kind: str,
        actor: CurrentUser | None = None,
    ) -> dict[str, object]:
        return self.platform_repository.add_call_message(session_id, body, kind, actor=actor)

    def get_livekit_connection(self, session_id: str, actor: CurrentUser | None = None) -> dict[str, str]:
        return self.platform_repository.get_livekit_connection(session_id, actor=actor)

    def get_access(self) -> dict[str, object]:
        return self.platform_repository.access()

    def get_settings(self) -> dict[str, object]:
        return self.platform_repository.settings()

    def get_settings_form(self) -> dict[str, str]:
        return self.platform_repository.get_settings_form()

    def update_settings(self, payload: dict[str, str], actor: CurrentUser | None = None) -> dict[str, str]:
        return self.platform_repository.update_settings(payload, actor=actor)

    def get_documents(self) -> dict[str, object]:
        return self.platform_repository.documents()
