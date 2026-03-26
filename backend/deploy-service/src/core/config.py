import os

from pydantic import BaseModel


class AppSettings(BaseModel):
    service_name: str = "deploy-service"
    service_version: str = "0.1.0"
    capabilities: list[str] = ["build", "deploy", "rollout"]
    kafka_bootstrap_servers: str = "kafka:9092"
    kafka_topic_prefix: str = "platform.local"
    log_level: str = "INFO"
    registry_endpoint: str = "http://registry:5000"
    retry_base_delay_ms: int = 250
    retry_max_attempts: int = 3
    storage_provider: str = "filesystem"
    storage_root: str = "/platform/storage"


def get_settings() -> AppSettings:
    return AppSettings(
        kafka_bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
        kafka_topic_prefix=os.getenv("KAFKA_TOPIC_PREFIX", "platform.local"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        registry_endpoint=os.getenv("REGISTRY_ENDPOINT", "http://registry:5000"),
        retry_base_delay_ms=int(os.getenv("RETRY_BASE_DELAY_MS", "250")),
        retry_max_attempts=int(os.getenv("RETRY_MAX_ATTEMPTS", "3")),
        storage_provider=os.getenv("STORAGE_PROVIDER", "filesystem"),
        storage_root=os.getenv("STORAGE_ROOT", "/platform/storage"),
    )
