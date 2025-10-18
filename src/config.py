"""Application configuration management using Pydantic Settings."""

from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # MongoDB Configuration
    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db: str = "books_scraper"

    # Crawler Configuration
    crawler_timeout: int = 30
    crawler_max_retries: int = 3
    crawler_backoff_factor: float = 2.0
    crawler_request_delay: float = 1.0
    crawler_target_url: str = "https://books.toscrape.com"

    # Scheduler Configuration
    scheduler_enabled: bool = True
    scheduler_interval_hours: int = 24
    scheduler_timezone: str = "UTC"

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4

    # Rate Limiting Configuration
    rate_limit_requests: int = 100
    rate_limit_period_seconds: int = 3600
    redis_url: str = "redis://localhost:6379"

    # Logging Configuration
    log_level: str = "INFO"
    log_file: str = "logs/app.log"

    # Alert Configuration
    alert_email_enabled: bool = False
    alert_email_to: Optional[str] = None
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None

    # API Keys (comma-separated)
    valid_api_keys: str = "test-key-123,test-key-456"

    class Config:
        """Pydantic config."""

        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
