"""Crawler engine with checkpoint support for resumable crawling."""

from typing import Any

from src.crawler.checkpoint import CheckpointManager
from src.crawler.client import AsyncHTTPClient
from src.crawler.parser import BookParser
from src.logger import crawler_logger


class CrawlerEngine:
    """Async crawler engine with checkpoint-based resume capability."""

    def __init__(
        self,
        db: Any,
        timeout: int = 30,
        max_retries: int = 3,
        backoff_factor: float = 2.0,
        request_delay: float = 1.0,
    ) -> None:
        """
        Initialize crawler engine.

        Args:
            db: Motor AsyncDatabase instance
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            backoff_factor: Exponential backoff factor
            request_delay: Delay between requests
        """
        self.db = db
        self.checkpoint_mgr = CheckpointManager(db)
        self.client_config = {
            "timeout": timeout,
            "max_retries": max_retries,
            "backoff_factor": backoff_factor,
            "request_delay": request_delay,
        }
        self.base_url = "https://books.toscrape.com"

    async def crawl(self, crawler_id: str = "default_crawl") -> None:
        """
        Perform full crawl with resume capability.

        Args:
            crawler_id: Unique identifier for this crawl run

        Raises:
            Exception: On fatal errors
        """
        # Load checkpoint if exists
        checkpoint = await self.checkpoint_mgr.load_checkpoint(crawler_id)
        start_page = checkpoint.get("last_page", 1) if checkpoint else 1

        crawler_logger.info(f"🚀 Starting crawl from page {start_page}")

        async with AsyncHTTPClient(**self.client_config) as client:
            page = start_page
            total_books = 0

            while True:
                try:
                    # Construct URL (books.toscrape.com uses page-N.html for pagination)
                    url = f"{self.base_url}/catalogue/page-{page}.html"

                    crawler_logger.debug(f"📄 Fetching page {page}")
                    response = await client.get(url)
                    html = response.text

                    # Parse books from listing page
                    books_meta = BookParser.parse_books_listing(html)

                    if not books_meta:
                        crawler_logger.info(f"✅ No books found on page {page}, ending crawl")
                        break

                    crawler_logger.info(f"📚 Found {len(books_meta)} books on page {page}")

                    # Fetch and parse each book detail page
                    for book_meta in books_meta:
                        try:
                            book_url = book_meta["url"]
                            detail_response = await client.get(book_url)
                            detail_html = detail_response.text

                            # Parse detail
                            book_detail = BookParser.parse_book_detail(detail_html, book_url)

                            if book_detail:
                                await self._save_book(book_detail)
                                total_books += 1
                                crawler_logger.debug(f"💾 Saved book: {book_detail['name']}")

                        except Exception as e:
                            crawler_logger.error(f"❌ Error crawling {book_meta.get('url')}: {e}")
                            continue

                    # Save checkpoint after successful page
                    await self.checkpoint_mgr.save_checkpoint(
                        crawler_id,
                        {"last_page": page, "status": "in_progress", "books_crawled": total_books},
                    )

                    page += 1

                except Exception as e:
                    crawler_logger.error(f"❌ Error on page {page}: {e}", exc_info=True)
                    # Save checkpoint for resume
                    await self.checkpoint_mgr.save_checkpoint(
                        crawler_id,
                        {
                            "last_page": page,
                            "status": "failed",
                            "error": str(e),
                            "books_crawled": total_books,
                        },
                    )
                    raise

        # Clear checkpoint on success
        await self.checkpoint_mgr.clear_checkpoint(crawler_id)
        crawler_logger.info(f"✅ Crawl completed successfully! Total books: {total_books}")

    async def _save_book(self, book_data: dict) -> None:
        """
        Save or update book in MongoDB.

        Args:
            book_data: Book data dictionary
        """
        from datetime import datetime
        
        collection = self.db["books"]
        
        # Add timestamps and status if not present
        book_data.setdefault("status", "active")
        book_data.setdefault("crawled_at", datetime.utcnow())
        book_data.setdefault("updated_at", datetime.utcnow())

        # Upsert by URL (unique constraint)
        result = await collection.update_one(
            {"url": book_data["url"]},
            {"$set": book_data},
            upsert=True,
        )

        if result.upserted_id:
            crawler_logger.debug(f"🆕 New book inserted: {book_data['url']}")
        elif result.modified_count:
            crawler_logger.debug(f"🔄 Book updated: {book_data['url']}")
