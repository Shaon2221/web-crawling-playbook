"""API middleware for authentication and rate limiting."""

import time

import redis
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from src.config import settings
from src.logger import api_logger


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Redis-backed rate limiting middleware."""

    def __init__(self, app) -> None:
        """Initialize rate limit middleware."""
        super().__init__(app)
        try:
            self.redis_client = redis.from_url(settings.redis_url, decode_responses=True)
            # Test connection
            self.redis_client.ping()
            api_logger.info("✅ Redis connected for rate limiting")
        except Exception as e:
            api_logger.warning(f"⚠️ Redis unavailable for rate limiting: {e}")
            self.redis_client = None

    async def dispatch(self, request: Request, call_next):
        """Rate limit by API key."""
        # Skip rate limiting for public endpoints
        public_paths = ["/health", "/docs", "/openapi.json", "/redoc"]
        if request.url.path in public_paths:
            return await call_next(request)

        if not self.redis_client:
            return await call_next(request)

        api_key = request.headers.get("X-API-Key", "anonymous")

        # Create rate limit key (hourly bucket)
        current_hour = int(time.time() // 3600)
        key = f"rate_limit:{api_key}:{current_hour}"

        try:
            # Increment counter
            count = self.redis_client.incr(key)

            # Set expiration on first request
            if count == 1:
                self.redis_client.expire(key, 3600)

            # Check limit
            if count > settings.rate_limit_requests:
                api_logger.warning(f"⚠️ Rate limit exceeded for {api_key}")
                return JSONResponse(
                    {"detail": "Rate limit exceeded (100 requests/hour)"},
                    status_code=429,
                )

            response = await call_next(request)
            response.headers["X-RateLimit-Limit"] = str(settings.rate_limit_requests)
            response.headers["X-RateLimit-Remaining"] = str(settings.rate_limit_requests - count)

            return response

        except Exception as e:
            api_logger.error(f"❌ Rate limit check failed: {e}")
            return await call_next(request)


class APIKeyMiddleware(BaseHTTPMiddleware):
    """Validate API key on all protected requests."""

    async def dispatch(self, request: Request, call_next):
        """Check API key on protected endpoints."""
        # Skip auth for public endpoints
        public_paths = ["/health", "/docs", "/openapi.json", "/redoc"]
        if request.url.path in public_paths:
            return await call_next(request)

        api_key = request.headers.get("X-API-Key")
        if not api_key:
            api_logger.warning(f"🚫 Missing API key for {request.url.path}")
            return JSONResponse(
                {"detail": "Missing X-API-Key header"},
                status_code=401,
            )

        valid_keys = [key.strip() for key in settings.valid_api_keys.split(",")]
        if api_key not in valid_keys:
            api_logger.warning(f"🚫 Invalid API key for {request.url.path}")
            return JSONResponse(
                {"detail": "Invalid API key"},
                status_code=403,
            )

        return await call_next(request)
