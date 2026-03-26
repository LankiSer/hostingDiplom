from dataclasses import dataclass


@dataclass(slots=True)
class ProjectEntity:
    name: str
    environment: str
    status: str


@dataclass(slots=True)
class MicroserviceEntity:
    project: str
    service_name: str
    runtime: str
