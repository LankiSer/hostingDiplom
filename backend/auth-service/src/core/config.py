from pydantic import BaseModel


class AppSettings(BaseModel):
    service_name: str = "auth-service"
    service_version: str = "0.1.0"
    capabilities: list[str] = ["login", "jwt", "organizations"]


def get_settings() -> AppSettings:
    return AppSettings()
