from dataclasses import asdict

from src.core.config import get_settings
from src.events.topics import DEPLOY_TOPICS
from src.repositories.repository import DeploymentRepository
from src.schemas.contracts import DeploymentRequest, RuntimeDetectionRequest
from src.services.event_publisher import DeploymentEventPublisher
from src.services.retry import RetryPolicy
from src.services.runtime_detector import RuntimeDetector
from src.services.storage import FileStorage


class DeployService:
    def __init__(self, repository: DeploymentRepository | None = None) -> None:
        settings = get_settings()
        self.repository = repository or DeploymentRepository()
        self.event_publisher = DeploymentEventPublisher(settings.kafka_topic_prefix)
        self.retry_policy = RetryPolicy(
            max_attempts=settings.retry_max_attempts,
            base_delay_ms=settings.retry_base_delay_ms,
        )
        self.runtime_detector = RuntimeDetector()
        self.storage = FileStorage(settings.storage_root)

    def create_deployment(self, payload: DeploymentRequest) -> dict[str, str | int]:
        detected_runtime = payload.runtime or self.runtime_detector.detect(
            RuntimeDetectionRequest(files=[payload.source_uri])
        )["runtime"]
        deployment_id = "deploy-001"
        artifact_path, attempt_count = self.retry_policy.run(
            lambda: self.storage.persist_source_reference(deployment_id, payload.source_uri)
        )
        deployment = self.repository.create_deployment(
            artifact_path=artifact_path,
            attempt_count=attempt_count,
            project=payload.project,
            runtime=detected_runtime,
            source_type=payload.source_type,
            source_uri=payload.source_uri,
        )
        response = asdict(deployment)
        self.event_publisher.publish(DEPLOY_TOPICS["deployment_created"], response)
        return response

    def detect_runtime(self, payload: RuntimeDetectionRequest) -> dict[str, str]:
        runtime = self.runtime_detector.detect(payload)
        self.event_publisher.publish(DEPLOY_TOPICS["runtime_detected"], runtime)
        return runtime

    def get_deployment(self, deployment_id: str) -> dict[str, str | int]:
        return asdict(self.repository.get_deployment(deployment_id))
