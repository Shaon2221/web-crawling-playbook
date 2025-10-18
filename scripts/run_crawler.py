#!/usr/bin/env python
"""One-time crawler invocation script."""

import asyncio

from src.config import settings
from src.crawler.storage import CrawlerEngine
from src.db.mongo import MongoDBManager
from src.logger import crawler_logger


async def main() -> None:
    """Run crawler once."""
    db_manager = MongoDBManager(settings.mongo_uri, settings.mongo_db)
    await db_manager.connect()

    try:
        engine = CrawlerEngine(
            db_manager.db,
            timeout=settings.crawler_timeout,
            max_retries=settings.crawler_max_retries,
            backoff_factor=settings.crawler_backoff_factor,
            request_delay=settings.crawler_request_delay,
        )
        await engine.crawl(crawler_id="manual_crawl")
        crawler_logger.info("✅ Crawl completed successfully")

    except Exception as e:
        crawler_logger.error(f"❌ Crawl failed: {e}", exc_info=True)
        raise

    finally:
        await db_manager.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
