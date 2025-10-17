"""Async web crawler with retry and resume capabilities."""

import asyncio
from datetime import datetime
from typing import Optional, Set
from urllib.parse import urljoin

import aiohttp
from aiohttp import ClientSession, ClientTimeout

from src.config import settings
from src.crawler.checkpoint import CheckpointManager
from src.crawler.parser import BookParser
from src.database import db_client
from src.database.models import BookModel
from src.utils import logger


class BooksCrawler:
    """Async crawler for Books to Scrape website."""

    def __init__(self) -> None:
        """Initialize crawler."""
        self.base_url = settings.crawler_base_url
        self.max_concurrent = settings.crawler_max_concurrent_requests
        self.request_delay = settings.crawler_request_delay
        self.max_retries = settings.crawler_max_retries
        self.timeout = settings.crawler_timeout
        self.user_agent = settings.crawler_user_agent

        self.checkpoint = CheckpointManager()
        self.parser = BookParser()
        self.session: Optional[ClientSession] = None
        self.semaphore = asyncio.Semaphore(self.max_concurrent)

        # Stats
        self.start_time: Optional[datetime] = None
        self.stats = {
            "successful_requests": 0,
            "failed_requests": 0,
            "books_scraped": 0,
            "pages_crawled": 0,
        }

    async def __aenter__(self) -> "BooksCrawler":
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.stop()

    async def start(self) -> None:
        """Start crawler session."""
        timeout = ClientTimeout(total=self.timeout)
        headers = {"User-Agent": self.user_agent}

        self.session = aiohttp.ClientSession(timeout=timeout, headers=headers)
        await db_client.connect()

        # Load checkpoint if enabled
        if settings.checkpoint_enabled:
            await self.checkpoint.load()

        self.start_time = datetime.utcnow()
        logger.info("Crawler started")

    async def stop(self) -> None:
        """Stop crawler and cleanup."""
        if self.session:
            await self.session.close()

        # Save final checkpoint
        if settings.checkpoint_enabled:
            await self.checkpoint.save(force=True)

        logger.info("Crawler stopped")

    async def fetch_url(self, url: str, retries: int = 0) -> Optional[str]:
        """
        Fetch URL with retry logic.

        Args:
            url: URL to fetch
            retries: Current retry count

        Returns:
            HTML content or None
        """
        if not self.session:
            raise RuntimeError("Crawler not started")

        async with self.semaphore:
            try:
                # Add delay between requests
                if self.request_delay > 0:
                    await asyncio.sleep(self.request_delay)

                async with self.session.get(url) as response:
                    response.raise_for_status()
                    self.stats["successful_requests"] += 1
                    logger.debug(f"Fetched: {url}")
                    return await response.text()

            except Exception as e:
                self.stats["failed_requests"] += 1
                logger.warning(f"Error fetching {url}: {e}")

                # Retry logic
                if retries < self.max_retries:
                    wait_time = 2 ** retries  # Exponential backoff
                    logger.info(f"Retrying {url} in {wait_time}s (attempt {retries + 1})")
                    await asyncio.sleep(wait_time)
                    return await self.fetch_url(url, retries + 1)
                else:
                    logger.error(f"Failed to fetch {url} after {retries} retries")
                    await self.checkpoint.update_stats(errors=1)
                    return None

    async def crawl_book_detail(self, book_url: str) -> None:
        """
        Crawl individual book detail page.

        Args:
            book_url: Book detail page URL
        """
        # Check if already visited
        if await self.checkpoint.is_visited(book_url):
            logger.debug(f"Already visited: {book_url}")
            return

        html = await self.fetch_url(book_url)
        if not html:
            return

        # Parse book details
        book_data = self.parser.parse_book_detail(html, book_url, self.base_url)

        # Save to database
        try:
            book = BookModel(**book_data)
            await db_client.insert_or_update_book(book)

            self.stats["books_scraped"] += 1
            await self.checkpoint.mark_visited(book_url)
            await self.checkpoint.update_stats(books_scraped=1)
            await self.checkpoint.save()

            logger.info(f"Scraped book: {book_data.get('title', 'Unknown')}")

        except Exception as e:
            logger.error(f"Error saving book {book_url}: {e}")
            await self.checkpoint.update_stats(errors=1)

    async def crawl_listing_page(self, page_url: str, category: str = "All") -> Set[str]:
        """
        Crawl a listing page and extract book URLs.

        Args:
            page_url: Listing page URL
            category: Category name

        Returns:
            Set of book URLs found
        """
        html = await self.fetch_url(page_url)
        if not html:
            return set()

        # Parse book listings
        books = self.parser.parse_book_listing(html, self.base_url)
        book_urls = set()

        for book_info in books:
            book_url = book_info["url"]
            book_urls.add(book_url)

            # Update book with category
            book_info["category"] = category

        self.stats["pages_crawled"] += 1
        await self.checkpoint.update_stats(pages_crawled=1)
        await self.checkpoint.save()

        logger.info(f"Found {len(books)} books on {page_url}")
        return book_urls

    async def crawl_category(self, category_url: str, category_name: str) -> None:
        """
        Crawl all pages in a category.

        Args:
            category_url: Category listing URL
            category_name: Category name
        """
        # Check if category already completed
        if await self.checkpoint.is_category_completed(category_name):
            logger.info(f"Category already completed: {category_name}")
            return

        logger.info(f"Crawling category: {category_name}")
        current_url = category_url
        all_book_urls: Set[str] = set()

        while current_url:
            # Crawl listing page
            book_urls = await self.crawl_listing_page(current_url, category_name)
            all_book_urls.update(book_urls)

            # Get next page URL
            html = await self.fetch_url(current_url)
            if html:
                next_url = self.parser.get_next_page_url(html, current_url)
                current_url = next_url
            else:
                break

        # Crawl all book details concurrently
        tasks = [self.crawl_book_detail(url) for url in all_book_urls]
        await asyncio.gather(*tasks)

        # Mark category as completed
        await self.checkpoint.mark_category_completed(category_name)
        logger.info(f"Completed category: {category_name}")

    async def crawl_all(self) -> None:
        """Crawl all books from the website."""
        logger.info("Starting full crawl")

        # Fetch homepage to get categories
        html = await self.fetch_url(self.base_url)
        if not html:
            logger.error("Failed to fetch homepage")
            return

        # Get all categories
        categories = self.parser.get_category_urls(html, self.base_url)
        logger.info(f"Found {len(categories)} categories")

        # Crawl each category
        for category in categories:
            await self.crawl_category(category["url"], category["name"])

        # Print final stats
        end_time = datetime.utcnow()
        duration = (end_time - self.start_time).total_seconds() if self.start_time else 0

        logger.info("=" * 60)
        logger.info("Crawl completed!")
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info(f"Books scraped: {self.stats['books_scraped']}")
        logger.info(f"Pages crawled: {self.stats['pages_crawled']}")
        logger.info(f"Successful requests: {self.stats['successful_requests']}")
        logger.info(f"Failed requests: {self.stats['failed_requests']}")
        logger.info("=" * 60)

    async def resume_crawl(self) -> None:
        """Resume crawl from checkpoint."""
        logger.info("Resuming crawl from checkpoint")

        # Get pending URLs from checkpoint
        pending_urls = await self.checkpoint.get_pending_urls()

        if pending_urls:
            logger.info(f"Resuming with {len(pending_urls)} pending URLs")
            tasks = [self.crawl_book_detail(url) for url in pending_urls]
            await asyncio.gather(*tasks)
        else:
            logger.info("No pending URLs, starting fresh crawl")
            await self.crawl_all()
