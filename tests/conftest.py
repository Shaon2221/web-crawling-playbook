"""Pytest configuration and fixtures."""

import pytest
import asyncio
from typing import AsyncGenerator

from motor.motor_asyncio import AsyncIOMotorClient


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def test_db():
    """Create a test database instance."""
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["test_books_crawler"]

    yield db

    # Cleanup
    await client.drop_database("test_books_crawler")
    client.close()


@pytest.fixture
def sample_book_data():
    """Sample book data for testing."""
    return {
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
    }
