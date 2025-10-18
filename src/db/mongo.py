"""MongoDB connection and schema management."""

from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING, TEXT

from src.logger import app_logger


class MongoDBManager:
    """MongoDB connection pool and schema manager."""

    def __init__(self, uri: str, db_name: str) -> None:
        """Initialize MongoDB manager."""
        self.uri = uri
        self.db_name = db_name
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None

    async def connect(self) -> None:
        """Initialize MongoDB connection and create indices."""
        try:
            self.client = AsyncIOMotorClient(self.uri)
            self.db = self.client[self.db_name]

            # Test connection
            await self.db.command("ping")
            app_logger.info(f"✅ Connected to MongoDB: {self.db_name}")

            # Create indices for efficient querying
            await self._create_indices()

        except Exception as e:
            app_logger.error(f"❌ MongoDB connection failed: {e}", exc_info=True)
            raise

    async def _create_indices(self) -> None:
        """Create MongoDB indices for optimal query performance."""
        try:
            books_collection = self.db["books"]

            # Create indices
            await books_collection.create_index([("name", TEXT)])
            await books_collection.create_index([("category", ASCENDING)])
            await books_collection.create_index([("price_incl_tax", ASCENDING)])
            await books_collection.create_index([("rating", DESCENDING)])
            await books_collection.create_index([("url", ASCENDING)], unique=True)
            await books_collection.create_index([("content_hash", ASCENDING)])
            await books_collection.create_index([("updated_at", DESCENDING)])
            await books_collection.create_index([("status", ASCENDING)])

            app_logger.info("✅ MongoDB indices created")

            # Create indices on changes collection
            changes_collection = self.db["changes"]
            await changes_collection.create_index([("book_id", ASCENDING)])
            await changes_collection.create_index([("detected_at", DESCENDING)])
            await changes_collection.create_index([("change_type", ASCENDING)])

            # Create checkpoint indices
            checkpoint_collection = self.db["crawler_checkpoints"]
            await checkpoint_collection.create_index([("crawler_id", ASCENDING)], unique=True)

        except Exception as e:
            app_logger.error(f"❌ Failed to create indices: {e}", exc_info=True)
            raise

    async def disconnect(self) -> None:
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            app_logger.info("✅ MongoDB connection closed")

    async def health_check(self) -> bool:
        """Verify MongoDB connection is alive."""
        try:
            if self.db is None:
                return False
            await self.db.command("ping")
            return True
        except Exception as e:
            app_logger.warning(f"⚠️ MongoDB health check failed: {e}")
            return False
