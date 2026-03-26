from dataclasses import asdict

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

    def login(self, email: str, organization: str) -> dict[str, str]:
        return self.platform_repository.login(email=email, organization=organization)

    def register(
        self,
        company_name: str,
        contact_name: str,
        email: str,
        inn: str,
        accept_policy: bool,
        accept_personal_data: bool,
    ) -> dict[str, str]:
        if not accept_policy or not accept_personal_data:
            raise ValueError("Required legal consents were not accepted.")
        return self.platform_repository.register(
            company_name=company_name,
            contact_name=contact_name,
            email=email,
            inn=inn,
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

    def get_team(self) -> dict[str, object]:
        return self.platform_repository.team()

    def get_access(self) -> dict[str, object]:
        return self.platform_repository.access()

    def get_settings(self) -> dict[str, object]:
        return self.platform_repository.settings()

    def get_settings_form(self) -> dict[str, str]:
        return self.platform_repository.get_settings_form()

    def update_settings(self, payload: dict[str, str]) -> dict[str, str]:
        return self.platform_repository.update_settings(payload)

    def get_documents(self) -> dict[str, object]:
        return self.platform_repository.documents()
