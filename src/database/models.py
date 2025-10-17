"""Database models and schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl


class BookModel(BaseModel):
    """Book data model matching MongoDB schema."""

    url: str = Field(..., description="Book detail page URL")
    title: str = Field(..., description="Book title")
    price: float = Field(..., description="Price in GBP")
    availability: str = Field(..., description="Stock availability status")
    rating: int = Field(..., ge=0, le=5, description="Star rating (0-5)")
    category: str = Field(..., description="Book category")
    upc: Optional[str] = Field(None, description="Universal Product Code")
    product_type: Optional[str] = Field(None, description="Product type")
    price_excl_tax: Optional[float] = Field(None, description="Price excluding tax")
    price_incl_tax: Optional[float] = Field(None, description="Price including tax")
    tax: Optional[float] = Field(None, description="Tax amount")
    num_reviews: Optional[int] = Field(None, description="Number of reviews")
    description: Optional[str] = Field(None, description="Book description")
    image_url: Optional[str] = Field(None, description="Cover image URL")

    # Metadata
    first_scraped_at: datetime = Field(
        default_factory=datetime.utcnow, description="First scrape timestamp"
    )
    last_scraped_at: datetime = Field(
        default_factory=datetime.utcnow, description="Last scrape timestamp"
    )
    scrape_count: int = Field(default=1, description="Number of times scraped")
    price_history: list[dict] = Field(
        default_factory=list, description="Price change history"
    )

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "url": "https://books.toscrape.com/catalogue/book_1/index.html",
                "title": "A Light in the Attic",
                "price": 51.77,
                "availability": "In stock (22 available)",
                "rating": 3,
                "category": "Poetry",
                "upc": "a897fe39b1053632",
                "product_type": "Books",
                "price_excl_tax": 51.77,
                "price_incl_tax": 51.77,
                "tax": 0.00,
                "num_reviews": 0,
                "description": "A collection of poems...",
                "image_url": "https://books.toscrape.com/media/cache/...",
            }
        }


class CrawlStats(BaseModel):
    """Crawl statistics model."""

    total_books: int = Field(default=0, description="Total books crawled")
    total_categories: int = Field(default=0, description="Total categories found")
    total_pages: int = Field(default=0, description="Total pages crawled")
    successful_requests: int = Field(default=0, description="Successful requests")
    failed_requests: int = Field(default=0, description="Failed requests")
    start_time: Optional[datetime] = Field(None, description="Crawl start time")
    end_time: Optional[datetime] = Field(None, description="Crawl end time")
    duration_seconds: Optional[float] = Field(None, description="Crawl duration")

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "total_books": 1000,
                "total_categories": 50,
                "total_pages": 50,
                "successful_requests": 1050,
                "failed_requests": 5,
                "start_time": "2024-01-01T00:00:00",
                "end_time": "2024-01-01T00:10:00",
                "duration_seconds": 600.5,
            }
        }
