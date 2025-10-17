"""Configuration management using Pydantic settings."""

from typing import List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # MongoDB Configuration
    mongodb_url: str = Field(default="mongodb://localhost:27017")
    mongodb_db_name: str = Field(default="books_crawler")
    mongodb_collection: str = Field(default="books")

    # Crawler Configuration
    crawler_base_url: str = Field(default="https://books.toscrape.com")
    crawler_max_concurrent_requests: int = Field(default=10, ge=1, le=100)
    crawler_request_delay: float = Field(default=0.5, ge=0)
    crawler_max_retries: int = Field(default=3, ge=0, le=10)
    crawler_timeout: int = Field(default=30, ge=1)
    crawler_user_agent: str = Field(
        default="BooksBot/1.0 (+https://github.com/yourusername/books-crawler)"
    )

    # Checkpoint/Resume Configuration
    checkpoint_enabled: bool = Field(default=True)
    checkpoint_file: str = Field(default="data/checkpoints/crawler_state.json")
    checkpoint_interval: int = Field(default=10, ge=1)

    # Scheduler Configuration
    scheduler_enabled: bool = Field(default=True)
    scheduler_interval_hours: int = Field(default=24, ge=1)
    scheduler_timezone: str = Field(default="UTC")

    # API Configuration
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000, ge=1024, le=65535)
    api_reload: bool = Field(default=False)
    api_workers: int = Field(default=4, ge=1)

    # API Security
    api_key_header: str = Field(default="X-API-Key")
    api_keys: str = Field(default="")

    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True)
    rate_limit_per_minute: int = Field(default=60, ge=1)

    # Logging Configuration
    log_level: str = Field(default="INFO")
    log_file: str = Field(default="logs/crawler.log")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    log_max_bytes: int = Field(default=10485760)
    log_backup_count: int = Field(default=5)

    # Application Environment
    environment: str = Field(default="production")
    debug: bool = Field(default=False)

    @field_validator("api_keys")
    @classmethod
    def validate_api_keys(cls, v: str) -> str:
        """Validate API keys are provided."""
        if not v.strip():
            raise ValueError("At least one API key must be provided")
        return v

    def get_api_keys_list(self) -> List[str]:
        """Return API keys as a list."""
        return [key.strip() for key in self.api_keys.split(",") if key.strip()]


# Global settings instance
settings = Settings()
