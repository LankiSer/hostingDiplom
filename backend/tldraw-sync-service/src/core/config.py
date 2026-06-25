"""Configuration for tldraw sync service."""
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Service settings."""
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
    service_name: str = "tldraw-sync-service"
    service_version: str = "0.1.0"
    
    log_level: str = Field(default="INFO")
    
    postgres_url: str = Field(
        default="postgresql://platform:platform@localhost:5432/platform"
    )
    
    sync_host: str = Field(default="0.0.0.0")
    sync_port: int = Field(default=8000)
    
    livekit_url: str = Field(default="http://livekit:7880")
    livekit_api_key: str = Field(default="")
    livekit_api_secret: str = Field(default="")


def get_settings() -> Settings:
    """Get settings instance."""
    return Settings()
