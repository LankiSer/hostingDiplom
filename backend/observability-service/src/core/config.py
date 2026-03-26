from pydantic import BaseModel


class AppSettings(BaseModel):
    service_name: str = "observability-service"
    service_version: str = "0.1.0"
    capabilities: list[str] = ["logs", "events", "audits"]


def get_settings() -> AppSettings:
    return AppSettings()
