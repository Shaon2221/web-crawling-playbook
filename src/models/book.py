"""Pydantic data models for books and API responses."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class BookStatus(str, Enum):
    """Book status enum."""

    ACTIVE = "active"
    UNAVAILABLE = "unavailable"
    REMOVED = "removed"


class Book(BaseModel):
    """Pydantic model for a book with all required fields."""

    id: Optional[str] = Field(None, alias="_id")
    url: str = Field(..., description="Original book URL")
    name: str = Field(..., min_length=1, description="Book name/title")
    description: Optional[str] = Field(None, max_length=5000, description="Book description")
    category: str = Field(..., description="Book category")
    price_incl_tax: float = Field(..., ge=0, description="Price including tax")
    price_excl_tax: float = Field(..., ge=0, description="Price excluding tax")
    availability: str = Field(..., description="Availability status")
    num_reviews: int = Field(default=0, ge=0, description="Number of reviews")
    rating: float = Field(..., ge=0, le=5, description="Book rating (0-5)")
    image_url: Optional[HttpUrl] = Field(None, description="URL to book cover image")
    raw_html: str = Field(..., description="Full HTML snapshot of book page")
    status: BookStatus = Field(default=BookStatus.ACTIVE, description="Book status")

    crawled_at: datetime = Field(default_factory=datetime.utcnow, description="Crawl timestamp")
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="Last update timestamp"
    )
    content_hash: str = Field(..., description="SHA256 hash of content for change detection")

    class Config:
        """Pydantic config."""

        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class BookResponse(BaseModel):
    """Response model for API (excludes raw_html)."""

    id: str = Field(..., alias="_id")
    url: str
    name: str
    description: Optional[str] = None
    category: str
    price_incl_tax: float
    price_excl_tax: float
    availability: str
    num_reviews: int
    rating: float
    image_url: Optional[str] = None
    status: BookStatus = Field(default=BookStatus.ACTIVE)
    crawled_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        """Pydantic config."""

        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat() if v else None}


class BookChange(BaseModel):
    """Model for tracked book changes."""

    id: Optional[str] = Field(None, alias="_id")
    book_id: str = Field(..., description="ID of changed book")
    book_url: str = Field(..., description="URL of changed book")
    change_type: str = Field(
        ..., description="Type of change (new, price_changed, availability_changed, rating_changed)"
    )
    old_value: Optional[dict] = Field(None, description="Previous values")
    new_value: Optional[dict] = Field(None, description="New values")
    detected_at: datetime = Field(
        default_factory=datetime.utcnow, description="Change detection timestamp"
    )
    crawler_run_id: Optional[str] = Field(
        None, description="ID of crawler run that detected change"
    )

    class Config:
        """Pydantic config."""

        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}
