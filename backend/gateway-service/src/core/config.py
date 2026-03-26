from pydantic import BaseModel


class AppSettings(BaseModel):
    service_name: str = "gateway-service"
    service_version: str = "0.1.0"
    allowed_origins: list[str] = [
        "http://dashboard.gcloude.local",
        "http://dashboard.gcloude.ru",
        "http://localhost",
        "http://localhost:3000",
    ]
    capabilities: list[str] = [
        "auth-service",
        "user-service",
        "project-service",
        "deploy-service",
        "domain-service",
        "billing-service",
        "observability-service",
    ]


def get_settings() -> AppSettings:
    return AppSettings()
