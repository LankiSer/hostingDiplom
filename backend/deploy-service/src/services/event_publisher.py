import logging


class DeploymentEventPublisher:
    def __init__(self, topic_prefix: str) -> None:
        self.logger = logging.getLogger("deploy-service.events")
        self.topic_prefix = topic_prefix

    def publish(self, topic: str, payload: dict[str, str | int]) -> None:
        self.logger.info(
            "publishing event",
            extra={
                "event_payload": payload,
                "event_topic": f"{self.topic_prefix}.{topic}",
            },
        )
