"""Unit tests for database models."""

import pytest
from datetime import datetime
from pydantic import ValidationError

from src.database.models import BookModel, CrawlStats


def test_book_model_valid():
    """Test valid book model creation."""
    book = BookModel(
        url="https://books.toscrape.com/catalogue/book_1/index.html",
        title="A Light in the Attic",
        price=51.77,
        availability="In stock",
        rating=3,
        category="Poetry",
    )

    assert book.url == "https://books.toscrape.com/catalogue/book_1/index.html"
    assert book.title == "A Light in the Attic"
    assert book.price == 51.77
    assert book.rating == 3
    assert book.category == "Poetry"
    assert book.scrape_count == 1
    assert isinstance(book.first_scraped_at, datetime)


def test_book_model_validation():
    """Test book model validation."""
    # Invalid rating
    with pytest.raises(ValidationError):
        BookModel(
            url="https://books.toscrape.com/catalogue/book_1/index.html",
            title="Test Book",
            price=10.0,
            availability="In stock",
            rating=6,  # Invalid: must be 0-5
            category="Fiction",
        )

    # Missing required fields
    with pytest.raises(ValidationError):
        BookModel(
            url="https://books.toscrape.com/catalogue/book_1/index.html",
            title="Test Book",
            # Missing price
            availability="In stock",
            rating=3,
            category="Fiction",
        )


def test_book_model_optional_fields():
    """Test book model with optional fields."""
    book = BookModel(
        url="https://books.toscrape.com/catalogue/book_1/index.html",
        title="Test Book",
        price=25.99,
        availability="In stock",
        rating=4,
        category="Fiction",
        upc="abc123",
        description="A great book",
        num_reviews=10,
    )

    assert book.upc == "abc123"
    assert book.description == "A great book"
    assert book.num_reviews == 10


def test_crawl_stats_model():
    """Test crawl stats model."""
    stats = CrawlStats(
        total_books=100,
        total_categories=10,
        total_pages=50,
        successful_requests=150,
        failed_requests=5,
    )

    assert stats.total_books == 100
    assert stats.total_categories == 10
    assert stats.successful_requests == 150
    assert stats.failed_requests == 5


def test_crawl_stats_defaults():
    """Test crawl stats default values."""
    stats = CrawlStats()

    assert stats.total_books == 0
    assert stats.total_categories == 0
    assert stats.total_pages == 0
