"""FastAPI authentication module with API key verification."""

from typing import Optional

from fastapi import Header, HTTPException, status

from src.config import settings
from src.logger import api_logger


async def verify_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    """
    Verify API key from request header.

    Args:
        x_api_key: API key from X-API-Key header

    Returns:
        Verified API key

    Raises:
        HTTPException: If API key is missing or invalid
    """
    if not x_api_key:
        api_logger.warning("🚫 Missing API key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-API-Key header",
        )

    valid_keys = [key.strip() for key in settings.valid_api_keys.split(",")]
    if x_api_key not in valid_keys:
        api_logger.warning(f"🚫 Invalid API key: {x_api_key[:10]}...")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )

    return x_api_key
