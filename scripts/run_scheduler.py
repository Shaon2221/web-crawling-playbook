#!/usr/bin/env python
"""Start APScheduler daemon for daily crawl jobs."""

import asyncio

from src.config import settings
from src.db.mongo import MongoDBManager
from src.logger import scheduler_logger
from src.scheduler.tasks import SchedulerManager


async def main() -> None:
    """Start scheduler."""
    db_manager = MongoDBManager(settings.mongo_uri, settings.mongo_db)
    await db_manager.connect()

    try:
        scheduler_mgr = SchedulerManager(
            db_manager.db,
            {
                "timeout": settings.crawler_timeout,
                "max_retries": settings.crawler_max_retries,
                "backoff_factor": settings.crawler_backoff_factor,
                "request_delay": settings.crawler_request_delay,
            },
        )

        scheduler_mgr.start()
        scheduler_logger.info("✅ Scheduler started. Press Ctrl+C to exit.")

        # Keep running
        await asyncio.Event().wait()

    except KeyboardInterrupt:
        scheduler_logger.info("⏹️ Scheduler stopped by user")

    except Exception as e:
        scheduler_logger.error(f"❌ Scheduler error: {e}", exc_info=True)
        raise

    finally:
        scheduler_mgr.shutdown()
        await db_manager.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
