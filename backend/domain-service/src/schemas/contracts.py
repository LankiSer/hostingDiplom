from pydantic import BaseModel


class DomainAssignmentRequest(BaseModel):
    service_name: str
    subdomain: str


class DomainAssignmentResponse(BaseModel):
    service_name: str
    subdomain: str
    ssl: str


class SslStatusResponse(BaseModel):
    service_name: str
    ssl: str
    status: str


class WildcardResponse(BaseModel):
    pattern: str
    ssl_strategy: str
