from dataclasses import asdict

from src.repositories.repository import DomainRepository
from src.schemas.contracts import DomainAssignmentRequest


class DomainService:
    def __init__(self, repository: DomainRepository | None = None) -> None:
        self.repository = repository or DomainRepository()

    def assign_domain(self, payload: DomainAssignmentRequest) -> dict[str, str]:
        return asdict(self.repository.assign_domain(payload.service_name, payload.subdomain))

    def get_ssl_status(self, service_name: str) -> dict[str, str]:
        return asdict(self.repository.get_ssl_status(service_name))

    def get_wildcard(self) -> dict[str, str]:
        return {"pattern": "*.apps.gcloude.ru", "ssl_strategy": "wildcard"}
