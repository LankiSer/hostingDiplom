from dataclasses import dataclass


@dataclass(slots=True)
class DomainEntity:
    service_name: str
    subdomain: str
    ssl: str


@dataclass(slots=True)
class SslEntity:
    service_name: str
    ssl: str
    status: str
