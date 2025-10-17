"""MongoDB database client and operations."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError

from src.config import settings
from src.database.models import BookModel, CrawlStats
from src.utils import logger


class DatabaseClient:
    """MongoDB client for managing book data."""

    def __init__(self) -> None:
        """Initialize database client."""
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
        self.collection: Optional[AsyncIOMotorCollection] = None

    async def connect(self) -> None:
        """Connect to MongoDB and create indexes."""
        try:
            self.client = AsyncIOMotorClient(settings.mongodb_url)
            self.db = self.client[settings.mongodb_db_name]
            self.collection = self.db[settings.mongodb_collection]

            # Create indexes for better query performance
            await self.collection.create_index([("url", ASCENDING)], unique=True)
            await self.collection.create_index([("title", ASCENDING)])
            await self.collection.create_index([("category", ASCENDING)])
            await self.collection.create_index([("price", ASCENDING)])
            await self.collection.create_index([("last_scraped_at", DESCENDING)])

            logger.info(f"Connected to MongoDB: {settings.mongodb_db_name}")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    async def disconnect(self) -> None:
        """Disconnect from MongoDB."""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")

    async def insert_or_update_book(self, book: BookModel) -> bool:
        """
        Insert a new book or update existing one.

        Args:
            book: Book data to insert/update

        Returns:
            True if inserted, False if updated
        """
        if not self.collection:
            raise RuntimeError("Database not connected")

        book_dict = book.model_dump()

        try:
            # Try to get existing book
            existing_book = await self.collection.find_one({"url": book.url})

            if existing_book:
                # Update existing book
                update_data = {
                    "$set": {
                        **book_dict,
                        "last_scraped_at": datetime.utcnow(),
                    },
                    "$inc": {"scrape_count": 1},
                }

                # Track price changes
                if existing_book.get("price") != book.price:
                    price_change = {
                        "price": book.price,
                        "changed_at": datetime.utcnow(),
                    }
                    update_data["$push"] = {"price_history": price_change}

                await self.collection.update_one({"url": book.url}, update_data)
                logger.debug(f"Updated book: {book.title}")
                return False
            else:
                # Insert new book
                await self.collection.insert_one(book_dict)
                logger.debug(f"Inserted new book: {book.title}")
                return True

        except DuplicateKeyError:
            logger.warning(f"Duplicate book found: {book.url}")
            return False
        except Exception as e:
            logger.error(f"Error inserting/updating book: {e}")
            raise

    async def get_book_by_url(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Get book by URL.

        Args:
            url: Book URL

        Returns:
            Book data or None
        """
        if not self.collection:
            raise RuntimeError("Database not connected")

        return await self.collection.find_one({"url": url})

    async def get_books(
        self,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get books with optional filtering.

        Args:
            skip: Number of documents to skip
            limit: Maximum number of documents to return
            category: Filter by category
            min_price: Minimum price filter
            max_price: Maximum price filter

        Returns:
            List of books
        """
        if not self.collection:
            raise RuntimeError("Database not connected")

        query: Dict[str, Any] = {}

        if category:
            query["category"] = category

        if min_price is not None or max_price is not None:
            query["price"] = {}
            if min_price is not None:
                query["price"]["$gte"] = min_price
            if max_price is not None:
                query["price"]["$lte"] = max_price

        cursor = self.collection.find(query).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)

    async def get_stats(self) -> CrawlStats:
        """
        Get crawling statistics.

        Returns:
            Crawl statistics
        """
        if not self.collection:
            raise RuntimeError("Database not connected")

        total_books = await self.collection.count_documents({})

        # Get unique categories
        categories = await self.collection.distinct("category")

        # Get first and last scrape times
        first_book = await self.collection.find_one(sort=[("first_scraped_at", ASCENDING)])
        last_book = await self.collection.find_one(sort=[("last_scraped_at", DESCENDING)])

        start_time = first_book["first_scraped_at"] if first_book else None
        end_time = last_book["last_scraped_at"] if last_book else None

        duration = None
        if start_time and end_time:
            duration = (end_time - start_time).total_seconds()

        return CrawlStats(
            total_books=total_books,
            total_categories=len(categories),
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration,
        )

    async def clear_all_books(self) -> int:
        """
        Clear all books from database.

        Returns:
            Number of deleted documents
        """
        if not self.collection:
            raise RuntimeError("Database not connected")

        result = await self.collection.delete_many({})
        logger.info(f"Cleared {result.deleted_count} books from database")
        return result.deleted_count


# Global database client instance
db_client = DatabaseClient()
