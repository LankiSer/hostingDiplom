from dataclasses import dataclass


@dataclass(slots=True)
class UserSession:
    email: str
    token: str
    token_type: str


@dataclass(slots=True)
class OrganizationEntity:
    company_name: str
    email: str
    inn: str
    status: str
