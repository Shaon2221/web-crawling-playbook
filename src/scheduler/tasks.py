"""Scheduler tasks for daily crawl and change detection."""

from datetime import datetime
from typing import Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.crawler.storage import CrawlerEngine
from src.logger import scheduler_logger
from src.scheduler.alerts import AlertManager
from src.scheduler.change_detector import ChangeDetector


class SchedulerManager:
    """APScheduler manager with in-memory job store.

    NOTE: Production deployments should use a sync MongoDB connection
    for the job store, separate from the async Motor database used by
    the crawler and API. This requires creating a separate pymongo client.
    """

    def __init__(self, db: Any, crawler_config: dict) -> None:
        """
        Initialize scheduler manager.

        Args:
            db: Motor AsyncDatabase instance
            crawler_config: Configuration for crawler engine
        """
        self.db = db
        self.crawler_config = crawler_config
        self.scheduler = AsyncIOScheduler()

        # Use in-memory job store for simplicity
        # Production should use MongoDBJobStore with sync pymongo connection
        self.scheduler.configure(
            executors={"default": {"type": "asyncio"}},
            timezone="UTC",
        )

    def start(self) -> None:
        """Start scheduler and register jobs."""
        scheduler_logger.info("🚀 Starting APScheduler")
        self.scheduler.start()

        # Schedule daily crawl at 2 AM UTC
        self.scheduler.add_job(
            self._daily_crawl_job,
            "cron",
            hour=2,
            minute=0,
            id="daily_crawl",
            name="Daily book crawl with change detection",
            replace_existing=True,
        )

        scheduler_logger.info("✅ Daily crawl job scheduled for 02:00 UTC")

    def shutdown(self) -> None:
        """Graceful shutdown."""
        scheduler_logger.info("⏹️ Shutting down scheduler")
        try:
            self.scheduler.shutdown(wait=True)
        except Exception as e:
            scheduler_logger.error(f"Error during scheduler shutdown: {e}")

    async def _daily_crawl_job(self) -> None:
        """Daily crawl with change detection."""
        crawler_id = f"daily_crawl_{datetime.utcnow().isoformat()}"
        scheduler_logger.info(f"🔄 Starting daily crawl job: {crawler_id}")

        try:
            # Run crawler
            engine = CrawlerEngine(self.db, **self.crawler_config)
            await engine.crawl(crawler_id=crawler_id)

            # Detect changes
            detector = ChangeDetector(self.db)
            changes = await detector.detect_all_changes()

            scheduler_logger.info(f"✅ Detected {len(changes)} changes")

            # Alert on changes
            if changes:
                alert_mgr = AlertManager()
                await alert_mgr.send_alert(changes)

        except Exception as e:
            scheduler_logger.error(f"❌ Daily crawl job failed: {e}", exc_info=True)
