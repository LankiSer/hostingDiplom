from src.domain.entities import MicroserviceEntity, ProjectEntity


class ProjectRepository:
    def list_projects(self) -> list[ProjectEntity]:
        return [ProjectEntity(name="billing-core", environment="production", status="active")]

    def create_project(self, name: str, environment: str) -> ProjectEntity:
        return ProjectEntity(name=name, environment=environment, status="created")

    def create_microservice(
        self,
        project: str,
        service_name: str,
        runtime: str,
    ) -> MicroserviceEntity:
        return MicroserviceEntity(project=project, service_name=service_name, runtime=runtime)
