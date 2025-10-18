"""Database-based checkpoint manager for resumable crawling."""

from datetime import datetime
from typing import Any, Dict, Optional

from src.logger import crawler_logger


class CheckpointManager:
    """Manage crawler checkpoints for resumable crawling."""

    def __init__(self, db: Any) -> None:
        """
        Initialize checkpoint manager.

        Args:
            db: Motor AsyncDatabase instance
        """
        self.db = db
        self.collection = db["crawler_checkpoints"]

    async def save_checkpoint(
        self,
        crawler_id: str,
        data: Dict[str, Any],
    ) -> None:
        """
        Save or update checkpoint.

        Args:
            crawler_id: Unique crawler run ID
            data: Checkpoint data (last_page, status, error, etc.)
        """
        checkpoint = {
            "crawler_id": crawler_id,
            "timestamp": datetime.utcnow(),
            **data,
        }
        await self.collection.update_one(
            {"crawler_id": crawler_id},
            {"$set": checkpoint},
            upsert=True,
        )
        crawler_logger.info(f"✅ Checkpoint saved for {crawler_id}: {data}")

    async def load_checkpoint(self, crawler_id: str) -> Optional[Dict[str, Any]]:
        """
        Load checkpoint or None if not found.

        Args:
            crawler_id: Unique crawler run ID

        Returns:
            Checkpoint data or None
        """
        doc = await self.collection.find_one({"crawler_id": crawler_id})
        if doc:
            crawler_logger.info(f"✅ Checkpoint loaded for {crawler_id}")
            return doc
        crawler_logger.info(f"ℹ️ No checkpoint found for {crawler_id}")
        return None

    async def clear_checkpoint(self, crawler_id: str) -> None:
        """
        Clear checkpoint after successful completion.

        Args:
            crawler_id: Unique crawler run ID
        """
        await self.collection.delete_one({"crawler_id": crawler_id})
        crawler_logger.info(f"✅ Checkpoint cleared for {crawler_id}")
