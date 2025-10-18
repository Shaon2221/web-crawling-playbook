"""Async HTTP client with exponential backoff retry strategy."""

import asyncio
import random
from typing import Optional

import httpx

from src.logger import crawler_logger


class RetryStrategy:
    """Exponential backoff retry strategy with jitter."""

    def __init__(self, max_retries: int = 3, backoff_factor: float = 2.0) -> None:
        """Initialize retry strategy."""
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

    def get_wait_time(self, attempt: int) -> float:
        """
        Calculate wait time with exponential backoff and jitter.

        Formula: backoff_factor^attempt + random(0, 1)

        Args:
            attempt: Retry attempt number (0-indexed)

        Returns:
            Wait time in seconds
        """
        wait = self.backoff_factor**attempt
        jitter = random.uniform(0, 1)
        return wait + jitter


class AsyncHTTPClient:
    """Async HTTP client with retry logic and connection pooling."""

    def __init__(
        self,
        timeout: int = 30,
        max_retries: int = 3,
        backoff_factor: float = 2.0,
        max_connections: int = 10,
        request_delay: float = 1.0,
    ) -> None:
        """
        Initialize async HTTP client.

        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
            backoff_factor: Exponential backoff factor
            max_connections: Maximum concurrent connections
            request_delay: Delay between requests in seconds
        """
        self.timeout = timeout
        self.retry_strategy = RetryStrategy(max_retries, backoff_factor)
        self.max_connections = max_connections
        self.request_delay = request_delay
        self.client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "AsyncHTTPClient":
        """Async context manager entry."""
        limits = httpx.Limits(
            max_connections=self.max_connections,
            max_keepalive_connections=5,
        )
        self.client = httpx.AsyncClient(
            limits=limits,
            timeout=self.timeout,
            headers={"User-Agent": "Books-Scraper/1.0 (+https://github.com)"},
        )
        return self

    async def __aexit__(self, *args) -> None:
        """Async context manager exit."""
        if self.client:
            await self.client.aclose()

    async def get(self, url: str, **kwargs) -> httpx.Response:
        """
        Perform GET request with automatic retries.

        Args:
            url: URL to fetch
            **kwargs: Additional arguments to pass to httpx

        Returns:
            Response object

        Raises:
            httpx.HTTPError: If all retries fail
        """
        for attempt in range(self.retry_strategy.max_retries + 1):
            try:
                # Add request delay (respect rate limits)
                await asyncio.sleep(self.request_delay)

                crawler_logger.debug(f"GET {url} (attempt {attempt + 1})")

                response = await self.client.get(url, **kwargs)
                response.raise_for_status()

                crawler_logger.info(f"✅ GET {url} - Status {response.status_code}")
                return response

            except httpx.TimeoutException as e:
                crawler_logger.warning(f"⏱️ Timeout on {url}: {e}")

            except httpx.HTTPStatusError as e:
                status_code = e.response.status_code
                # Retryable errors: rate limit, server errors
                if status_code in [429, 500, 502, 503, 504]:
                    crawler_logger.warning(f"🔄 Retryable error {status_code} on {url}")
                else:
                    crawler_logger.error(f"❌ Non-retryable error {status_code} on {url}")
                    raise

            except httpx.RequestError as e:
                crawler_logger.warning(f"❌ Request error on {url}: {e}")

            # Retry with backoff
            if attempt < self.retry_strategy.max_retries:
                wait_time = self.retry_strategy.get_wait_time(attempt)
                crawler_logger.info(f"⏳ Retrying {url} in {wait_time:.2f}s")
                await asyncio.sleep(wait_time)
            else:
                crawler_logger.error(f"❌ Max retries exceeded for {url}")
                raise httpx.ConnectError(
                    f"Failed to fetch {url} after {self.retry_strategy.max_retries} retries"
                )
