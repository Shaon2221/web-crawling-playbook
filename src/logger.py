"""Structured JSON logging configuration."""

import json
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from src.config import settings


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def setup_logger(name: str, log_file: str, level: str = "INFO") -> logging.Logger:
    """
    Configure and return a structured logger with file rotation.

    Args:
        name: Logger name
        log_file: Path to log file
        level: Log level (INFO, DEBUG, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Remove existing handlers
    logger.handlers.clear()

    # File handler with rotation (10 MB, keep 5 backups)
    file_handler = RotatingFileHandler(log_file, maxBytes=10_000_000, backupCount=5)
    file_handler.setFormatter(JSONFormatter())
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(JSONFormatter())
    logger.addHandler(console_handler)

    # Prevent propagation to root logger
    logger.propagate = False

    return logger


# Initialize module-specific loggers
app_logger: Optional[logging.Logger] = None
crawler_logger: Optional[logging.Logger] = None
scheduler_logger: Optional[logging.Logger] = None
api_logger: Optional[logging.Logger] = None


def initialize_loggers() -> None:
    """Initialize all application loggers."""
    global app_logger, crawler_logger, scheduler_logger, api_logger

    log_level = settings.log_level
    log_dir = Path(settings.log_file).parent

    app_logger = setup_logger("app", str(log_dir / "app.log"), log_level)
    crawler_logger = setup_logger("crawler", str(log_dir / "crawler.log"), log_level)
    scheduler_logger = setup_logger("scheduler", str(log_dir / "scheduler.log"), log_level)
    api_logger = setup_logger("api", str(log_dir / "api.log"), log_level)


# Initialize loggers on module import
initialize_loggers()
