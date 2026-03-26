from src.domain.entities import DeploymentEntity


class DeploymentRepository:
    def create_deployment(
        self,
        project: str,
        runtime: str,
        source_type: str,
        source_uri: str,
        artifact_path: str,
        attempt_count: int,
    ) -> DeploymentEntity:
        return DeploymentEntity(
            artifact_path=artifact_path,
            attempt_count=attempt_count,
            deployment_id="deploy-001",
            project=project,
            source_type=source_type,
            source_uri=source_uri,
            runtime=runtime,
            status="running",
            target="docker",
        )

    def get_deployment(self, deployment_id: str) -> DeploymentEntity:
        return DeploymentEntity(
            artifact_path="/platform/storage/deployments/deploy-001/source.txt",
            attempt_count=1,
            deployment_id=deployment_id,
            project="billing-core",
            source_type="git",
            source_uri="https://github.com/example/billing-core",
            runtime="python",
            status="running",
            target="docker",
        )
