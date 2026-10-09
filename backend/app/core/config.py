from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://navagents:navagents@localhost:5433/navagents"
    redis_url: str = "redis://localhost:6379/0"

    s3_endpoint_url: str = "http://localhost:9000"
    s3_access_key: str = "navagents"
    s3_secret_key: str = "navagents123"
    s3_bucket: str = "event-media"

    device_offline_queue_max_events: int = 500
    device_offline_queue_max_mb: int = 100


settings = Settings()
