"""Change detection logic comparing old and new book data."""

from datetime import datetime, timedelta
from typing import Any, Dict, List

from src.logger import scheduler_logger


class ChangeDetector:
    """Detect book changes using content hashing and field comparison."""

    def __init__(self, db: Any) -> None:
        """
        Initialize change detector.

        Args:
            db: Motor AsyncDatabase instance
        """
        self.db = db

    async def detect_all_changes(self) -> List[Dict[str, Any]]:
        """
        Detect all changes in current crawl compared to previous version.

        Returns:
            List of detected changes
        """
        books_collection = self.db["books"]
        changes_collection = self.db["changes"]
        changes = []

        # Get all books from current crawl
        async for book in books_collection.find({}):
            url = book.get("url")
            book_id = str(book.get("_id"))

            # Find previous version of this book
            previous_changes = await changes_collection.find_one(
                {"book_url": url},
                sort=[("detected_at", -1)],
            )

            if not previous_changes:
                # New book detected
                changes.append(
                    {
                        "book_id": book_id,
                        "book_url": url,
                        "change_type": "new",
                        "old_value": None,
                        "new_value": {
                            "name": book.get("name"),
                            "price_incl_tax": book.get("price_incl_tax"),
                            "rating": book.get("rating"),
                        },
                        "detected_at": datetime.utcnow(),
                    }
                )
                scheduler_logger.info(f"🆕 New book detected: {book.get('name')}")
            else:
                # Check for price changes
                old_price = previous_changes.get("new_value", {}).get("price_incl_tax")
                new_price = book.get("price_incl_tax")

                if old_price is not None and old_price != new_price:
                    changes.append(
                        {
                            "book_id": book_id,
                            "book_url": url,
                            "change_type": "price_changed",
                            "old_value": {"price_incl_tax": old_price},
                            "new_value": {"price_incl_tax": new_price},
                            "detected_at": datetime.utcnow(),
                        }
                    )
                    price_diff = new_price - old_price
                    msg = (
                        f"💰 Price changed for {book.get('name')}: "
                        f"£{old_price} → £{new_price} ({price_diff:+.2f})"
                    )
                    scheduler_logger.info(msg)

                # Check for availability changes
                old_avail = previous_changes.get("new_value", {}).get("availability")
                new_avail = book.get("availability")

                if old_avail is not None and old_avail != new_avail:
                    changes.append(
                        {
                            "book_id": book_id,
                            "book_url": url,
                            "change_type": "availability_changed",
                            "old_value": {"availability": old_avail},
                            "new_value": {"availability": new_avail},
                            "detected_at": datetime.utcnow(),
                        }
                    )
                    scheduler_logger.info(
                        f"📦 Availability changed for {book.get('name')}: {old_avail} → {new_avail}"
                    )

                # Check for rating changes
                old_rating = previous_changes.get("new_value", {}).get("rating")
                new_rating = book.get("rating")

                if old_rating is not None and old_rating != new_rating:
                    changes.append(
                        {
                            "book_id": book_id,
                            "book_url": url,
                            "change_type": "rating_changed",
                            "old_value": {"rating": old_rating},
                            "new_value": {"rating": new_rating},
                            "detected_at": datetime.utcnow(),
                        }
                    )
                    scheduler_logger.info(
                        f"⭐ Rating changed for {book.get('name')}: {old_rating} → {new_rating}"
                    )

        # Insert changes into log
        if changes:
            await changes_collection.insert_many(changes)
            scheduler_logger.info(f"✅ Logged {len(changes)} changes")
        else:
            scheduler_logger.info("✅ No changes detected")

        return changes

    async def get_recent_changes(self, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Retrieve changes from last N hours.

        Args:
            hours: Number of hours to look back

        Returns:
            List of changes
        """
        changes_collection = self.db["changes"]
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        changes = []
        cursor = changes_collection.find(
            {"detected_at": {"$gte": cutoff_time}},
            sort=[("detected_at", -1)],
        )

        async for change in cursor:
            changes.append(change)

        return changes
