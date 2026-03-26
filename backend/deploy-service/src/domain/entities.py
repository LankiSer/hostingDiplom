from dataclasses import dataclass


@dataclass(slots=True)
class DeploymentEntity:
    artifact_path: str
    attempt_count: int
    deployment_id: str
    project: str
    source_type: str
    source_uri: str
    runtime: str
    status: str
    target: str
