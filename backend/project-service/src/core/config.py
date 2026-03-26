from pydantic import BaseModel


class AppSettings(BaseModel):
    service_name: str = "project-service"
    service_version: str = "0.1.0"
    capabilities: list[str] = ["projects", "microservices", "environments"]


def get_settings() -> AppSettings:
    return AppSettings()
