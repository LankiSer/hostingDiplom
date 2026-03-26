from pydantic import BaseModel


class AppSettings(BaseModel):
    service_name: str = "billing-service"
    service_version: str = "0.1.0"
    capabilities: list[str] = ["invoices", "quotas", "one-c"]


def get_settings() -> AppSettings:
    return AppSettings()
