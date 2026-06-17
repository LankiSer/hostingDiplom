import os

from pydantic import BaseModel


class AppSettings(BaseModel):
    service_name: str = "gateway-service"
    service_version: str = "0.1.0"
    allowed_origins: list[str] = [
        "http://dashboard.gcloude.local",
        "http://dashboard.gcloude.ru",
        "http://localhost",
        "http://localhost:3000",
        "https://app.kostricyn.ru",
        "http://app.kostricyn.ru",
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
    raw = os.getenv("ALLOWED_ORIGINS", "")
    origins = [item.strip() for item in raw.split(",") if item.strip()]
    if origins:
        return AppSettings(allowed_origins=origins)
    return AppSettings()
