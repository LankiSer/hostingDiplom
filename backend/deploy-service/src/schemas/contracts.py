from pydantic import BaseModel


class DeploymentRequest(BaseModel):
    project: str
    runtime: str | None = None
    source_type: str = "git"
    source_uri: str


class DeploymentResponse(BaseModel):
    artifact_path: str
    attempt_count: int
    deployment_id: str
    project: str
    source_type: str
    source_uri: str
    runtime: str
    status: str
    target: str


class RuntimeDetectionRequest(BaseModel):
    files: list[str]


class RuntimeDetectionResponse(BaseModel):
    runtime: str
    strategy: str
