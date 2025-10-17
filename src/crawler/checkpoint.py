"""Checkpoint manager for crawler state persistence."""

import json
import asyncio
from pathlib import Path
from typing import Dict, Any, Set
from datetime import datetime

from src.config import settings
from src.utils import logger


class CheckpointManager:
    """Manages crawler state for resume capability."""

    def __init__(self, checkpoint_file: str = "") -> None:
        """
        Initialize checkpoint manager.

        Args:
            checkpoint_file: Path to checkpoint file
        """
        self.checkpoint_file = Path(checkpoint_file or settings.checkpoint_file)
        self.state: Dict[str, Any] = {
            "visited_urls": set(),
            "pending_urls": set(),
            "completed_categories": set(),
            "last_update": None,
            "stats": {
                "books_scraped": 0,
                "pages_crawled": 0,
                "errors": 0,
            },
        }
        self._lock = asyncio.Lock()
        self._save_counter = 0

    async def load(self) -> bool:
        """
        Load checkpoint from file.

        Returns:
            True if checkpoint loaded successfully
        """
        async with self._lock:
            try:
                if self.checkpoint_file.exists():
                    with open(self.checkpoint_file, "r") as f:
                        data = json.load(f)

                    # Convert lists back to sets
                    self.state["visited_urls"] = set(data.get("visited_urls", []))
                    self.state["pending_urls"] = set(data.get("pending_urls", []))
                    self.state["completed_categories"] = set(
                        data.get("completed_categories", [])
                    )
                    self.state["last_update"] = data.get("last_update")
                    self.state["stats"] = data.get("stats", self.state["stats"])

                    logger.info(
                        f"Loaded checkpoint: {len(self.state['visited_urls'])} visited URLs, "
                        f"{len(self.state['pending_urls'])} pending URLs"
                    )
                    return True
                else:
                    logger.info("No checkpoint file found, starting fresh")
                    return False

            except Exception as e:
                logger.error(f"Error loading checkpoint: {e}")
                return False

    async def save(self, force: bool = False) -> None:
        """
        Save checkpoint to file.

        Args:
            force: Force save regardless of interval
        """
        async with self._lock:
            self._save_counter += 1

            # Only save at intervals unless forced
            if not force and self._save_counter % settings.checkpoint_interval != 0:
                return

            try:
                # Ensure directory exists
                self.checkpoint_file.parent.mkdir(parents=True, exist_ok=True)

                # Convert sets to lists for JSON serialization
                data = {
                    "visited_urls": list(self.state["visited_urls"]),
                    "pending_urls": list(self.state["pending_urls"]),
                    "completed_categories": list(self.state["completed_categories"]),
                    "last_update": datetime.utcnow().isoformat(),
                    "stats": self.state["stats"],
                }

                # Write to temporary file first, then rename for atomic write
                temp_file = self.checkpoint_file.with_suffix(".tmp")
                with open(temp_file, "w") as f:
                    json.dump(data, f, indent=2)

                temp_file.replace(self.checkpoint_file)
                logger.debug(f"Saved checkpoint to {self.checkpoint_file}")

            except Exception as e:
                logger.error(f"Error saving checkpoint: {e}")

    async def mark_visited(self, url: str) -> None:
        """Mark URL as visited."""
        async with self._lock:
            self.state["visited_urls"].add(url)
            self.state["pending_urls"].discard(url)

    async def add_pending(self, urls: Set[str]) -> None:
        """Add URLs to pending set."""
        async with self._lock:
            # Only add URLs that haven't been visited
            new_urls = urls - self.state["visited_urls"]
            self.state["pending_urls"].update(new_urls)

    async def is_visited(self, url: str) -> bool:
        """Check if URL has been visited."""
        async with self._lock:
            return url in self.state["visited_urls"]

    async def get_pending_urls(self) -> Set[str]:
        """Get all pending URLs."""
        async with self._lock:
            return self.state["pending_urls"].copy()

    async def mark_category_completed(self, category: str) -> None:
        """Mark category as completed."""
        async with self._lock:
            self.state["completed_categories"].add(category)

    async def is_category_completed(self, category: str) -> bool:
        """Check if category has been completed."""
        async with self._lock:
            return category in self.state["completed_categories"]

    async def update_stats(self, **kwargs: Any) -> None:
        """Update statistics."""
        async with self._lock:
            for key, value in kwargs.items():
                if key in self.state["stats"]:
                    if isinstance(value, int):
                        self.state["stats"][key] += value
                    else:
                        self.state["stats"][key] = value

    async def get_stats(self) -> Dict[str, Any]:
        """Get current statistics."""
        async with self._lock:
            return self.state["stats"].copy()

    async def clear(self) -> None:
        """Clear checkpoint state."""
        async with self._lock:
            self.state = {
                "visited_urls": set(),
                "pending_urls": set(),
                "completed_categories": set(),
                "last_update": None,
                "stats": {
                    "books_scraped": 0,
                    "pages_crawled": 0,
                    "errors": 0,
                },
            }

            if self.checkpoint_file.exists():
                self.checkpoint_file.unlink()
                logger.info("Cleared checkpoint file")
