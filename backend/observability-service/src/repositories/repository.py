from src.domain.entities import EventEntity


class ObservabilityRepository:
    def list_events(self) -> list[EventEntity]:
        return [
            EventEntity(type="deploy.started", target="billing-core/api"),
            EventEntity(type="domain.assigned", target="api.apps.gcloude.ru"),
        ]

    def get_logs(self, service_name: str) -> dict[str, list[str] | str]:
        return {
            "service_name": service_name,
            "lines": ["container started", "healthcheck passed", "ssl attached"],
        }
