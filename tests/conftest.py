"""Pytest configuration and shared fixtures."""

import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from testcontainers.mongodb import MongoDbContainer


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def mongo_container() -> AsyncGenerator[MongoDbContainer, None]:
    """Start MongoDB container for tests."""
    container = MongoDbContainer(image="mongo:6.0")
    container.start()
    yield container
    container.stop()


@pytest_asyncio.fixture
async def async_db(
    mongo_container: MongoDbContainer,
) -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """Create async MongoDB client and database for tests."""
    client = AsyncIOMotorClient(mongo_container.get_connection_string())
    db = client["test_books"]
    yield db
    client.close()


@pytest.fixture
def sample_book_html() -> str:
    """Sample HTML for testing parser - book detail page."""
    return """
    <html>
        <head>
            <meta name="description" content="Sample book description">
        </head>
        <body>
            <h1>Test Book Title</h1>
            <table class="table table-striped">
                <tr>
                    <td>Price (excl. tax)</td>
                    <td>£10.00</td>
                </tr>
                <tr>
                    <td>Price (incl. tax)</td>
                    <td>£12.00</td>
                </tr>
            </table>
            <p class="star-rating Five">
                Five
            </p>
            <p class="star-rating">5 out of 5</p>
            <p class="instock availability">In stock (10 available)</p>
            <img src="media/cache/test.jpg" />
            <ul class="breadcrumb">
                <li><a href="#">Home</a></li>
                <li>Fiction</li>
                <li>Test Book</li>
            </ul>
        </body>
    </html>
    """


@pytest.fixture
def sample_listing_html() -> str:
    """Sample HTML for testing parser - listing page."""
    return """
    <html>
        <body>
            <article class="product_pod">
                <h3><a href="catalogue/book-1/index.html" title="Book One">Book One</a></h3>
                <p class="star-rating Three">Three</p>
                <p class="price_color">£10.00</p>
                <p class="instock availability">In stock (5 available)</p>
            </article>
            <article class="product_pod">
                <h3><a href="catalogue/book-2/index.html" title="Book Two">Book Two</a></h3>
                <p class="star-rating Four">Four</p>
                <p class="price_color">£15.00</p>
                <p class="instock availability">Out of stock</p>
            </article>
        </body>
    </html>
    """


@pytest.fixture
async def sample_books(async_db: AsyncIOMotorDatabase) -> list:
    """Insert sample books for API tests."""
    from datetime import datetime

    collection = async_db["books"]
    books = [
        {
            "url": "https://books.toscrape.com/catalogue/book-1/index.html",
            "name": "Python Basics",
            "category": "Technology",
            "price_incl_tax": 29.99,
            "price_excl_tax": 24.99,
            "availability": "In stock (5 available)",
            "num_reviews": 10,
            "rating": 4.5,
            "image_url": "https://example.com/1.jpg",
            "description": "Learn Python programming",
            "raw_html": "<html>...</html>",
            "status": "active",
            "content_hash": "abc123",
            "crawled_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        },
        {
            "url": "https://books.toscrape.com/catalogue/book-2/index.html",
            "name": "Advanced Python",
            "category": "Technology",
            "price_incl_tax": 49.99,
            "price_excl_tax": 39.99,
            "availability": "Out of stock",
            "num_reviews": 25,
            "rating": 4.8,
            "image_url": "https://example.com/2.jpg",
            "description": "Advanced Python concepts",
            "raw_html": "<html>...</html>",
            "status": "active",
            "content_hash": "def456",
            "crawled_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        },
    ]
    result = await collection.insert_many(books)
    return result.inserted_ids
