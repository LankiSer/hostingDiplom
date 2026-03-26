from dataclasses import asdict

from src.repositories.repository import ProjectRepository
from src.schemas.contracts import MicroserviceCreateRequest, ProjectCreateRequest


class ProjectService:
    def __init__(self, repository: ProjectRepository | None = None) -> None:
        self.repository = repository or ProjectRepository()

    def list_projects(self) -> list[dict[str, str]]:
        return [asdict(project) for project in self.repository.list_projects()]

    def create_project(self, payload: ProjectCreateRequest) -> dict[str, str]:
        project = self.repository.create_project(payload.name, payload.environment)
        return asdict(project)

    def create_microservice(self, payload: MicroserviceCreateRequest) -> dict[str, str]:
        service = self.repository.create_microservice(
            project=payload.project,
            service_name=payload.service_name,
            runtime=payload.runtime,
        )
        return asdict(service)
