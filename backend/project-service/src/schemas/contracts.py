from pydantic import BaseModel


class ProjectCreateRequest(BaseModel):
    environment: str
    name: str


class ProjectResponse(BaseModel):
    environment: str
    name: str
    status: str


class MicroserviceCreateRequest(BaseModel):
    project: str
    runtime: str
    service_name: str


class MicroserviceResponse(BaseModel):
    project: str
    runtime: str
    service_name: str
