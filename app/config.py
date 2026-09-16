from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Cloud Phone Bridge"
    app_env: str = "development"
    app_debug: bool = False
    database_url: str = "postgresql+asyncpg://bridge:bridge@postgres:5432/cloud_phone_bridge"
    redis_url: str = "redis://redis:6379/0"
    api_bearer_token: str = "change-me"
    vendor_request_timeout_seconds: int = 30
    adb_timeout_seconds: int = 60

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
