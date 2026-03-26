from pydantic import BaseModel


class AppSettings(BaseModel):
    service_name: str = "user-service"
    service_version: str = "0.1.0"
    capabilities: list[str] = ["users", "teams", "roles"]


def get_settings() -> AppSettings:
    return AppSettings()
