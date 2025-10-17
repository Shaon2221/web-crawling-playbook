"""Scheduler for periodic crawling and change detection."""

from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

from src.config import settings
from src.crawler import BooksCrawler
from src.database import db_client
from src.utils import logger


class CrawlScheduler:
    """Scheduler for periodic web crawling."""

    def __init__(self) -> None:
        """Initialize scheduler."""
        self.scheduler = AsyncIOScheduler(timezone=settings.scheduler_timezone)
        self.crawler: BooksCrawler | None = None
        self.is_running = False

    async def crawl_job(self) -> None:
        """Execute crawl job."""
        if self.is_running:
            logger.warning("Crawl already in progress, skipping this run")
            return

        self.is_running = True
        logger.info("Starting scheduled crawl")

        try:
            async with BooksCrawler() as crawler:
                self.crawler = crawler
                await crawler.crawl_all()

                # Get statistics
                stats = await db_client.get_stats()
                logger.info(f"Scheduled crawl completed: {stats.total_books} books in database")

        except Exception as e:
            logger.error(f"Error during scheduled crawl: {e}")
        finally:
            self.is_running = False
            self.crawler = None

    async def detect_changes_job(self) -> None:
        """Detect changes in book data (prices, availability, etc.)."""
        logger.info("Starting change detection")

        try:
            # Get all books and check for recent changes
            stats = await db_client.get_stats()

            # Count books with price changes
            if db_client.collection:
                books_with_price_changes = await db_client.collection.count_documents(
                    {"price_history": {"$ne": [], "$exists": True}}
                )

                logger.info(
                    f"Change detection completed: {books_with_price_changes} books "
                    f"with price changes out of {stats.total_books} total"
                )

        except Exception as e:
            logger.error(f"Error during change detection: {e}")

    def start(self) -> None:
        """Start the scheduler."""
        if not settings.scheduler_enabled:
            logger.info("Scheduler is disabled")
            return

        # Add periodic crawl job
        self.scheduler.add_job(
            self.crawl_job,
            trigger=IntervalTrigger(hours=settings.scheduler_interval_hours),
            id="periodic_crawl",
            name="Periodic Crawl",
            replace_existing=True,
        )

        # Add change detection job (runs more frequently)
        self.scheduler.add_job(
            self.detect_changes_job,
            trigger=IntervalTrigger(hours=1),
            id="change_detection",
            name="Change Detection",
            replace_existing=True,
        )

        self.scheduler.start()
        logger.info(
            f"Scheduler started: crawl interval={settings.scheduler_interval_hours}h, "
            f"timezone={settings.scheduler_timezone}"
        )

    def stop(self) -> None:
        """Stop the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=True)
            logger.info("Scheduler stopped")

    def get_jobs(self) -> list:
        """Get list of scheduled jobs."""
        return self.scheduler.get_jobs()

    def get_next_run_time(self, job_id: str) -> datetime | None:
        """Get next run time for a specific job."""
        job = self.scheduler.get_job(job_id)
        return job.next_run_time if job else None


# Global scheduler instance
scheduler = CrawlScheduler()
