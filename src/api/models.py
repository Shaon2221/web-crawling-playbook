"""API response models."""

from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, Field


class BookResponse(BaseModel):
    """Book response model."""

    url: str
    title: str
    price: float
    availability: str
    rating: int
    category: str
    upc: Optional[str] = None
    product_type: Optional[str] = None
    price_excl_tax: Optional[float] = None
    price_incl_tax: Optional[float] = None
    tax: Optional[float] = None
    num_reviews: Optional[int] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    first_scraped_at: datetime
    last_scraped_at: datetime
    scrape_count: int
    price_history: List[dict] = Field(default_factory=list)


class BooksListResponse(BaseModel):
    """Books list response with pagination."""

    books: List[BookResponse]
    total: int
    skip: int
    limit: int


class StatsResponse(BaseModel):
    """Crawl statistics response."""

    total_books: int
    total_categories: int
    total_pages: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None


class CrawlResponse(BaseModel):
    """Crawl operation response."""

    status: str
    message: str
    started_at: Optional[datetime] = None


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    timestamp: datetime
    database: str
    scheduler: str
    environment: str


class ErrorResponse(BaseModel):
    """Error response model."""

    detail: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
