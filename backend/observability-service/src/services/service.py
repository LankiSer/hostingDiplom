from dataclasses import asdict

from src.repositories.repository import ObservabilityRepository


class ObservabilityService:
    def __init__(self, repository: ObservabilityRepository | None = None) -> None:
        self.repository = repository or ObservabilityRepository()

    def list_events(self) -> list[dict[str, str]]:
        return [asdict(event) for event in self.repository.list_events()]

    def get_logs(self, service_name: str) -> dict[str, list[str] | str]:
        return self.repository.get_logs(service_name)
