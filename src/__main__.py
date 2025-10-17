"""Main entry point for the Books Crawler application."""

import asyncio
import argparse
import sys

from src.config import settings
from src.crawler import BooksCrawler
from src.database import db_client
from src.utils import logger


async def run_crawler(resume: bool = False) -> None:
    """
    Run the crawler.

    Args:
        resume: Resume from checkpoint if available
    """
    async with BooksCrawler() as crawler:
        if resume:
            await crawler.resume_crawl()
        else:
            await crawler.crawl_all()


async def show_stats() -> None:
    """Show crawling statistics."""
    await db_client.connect()
    try:
        stats = await db_client.get_stats()
        print("\n" + "=" * 60)
        print("CRAWL STATISTICS")
        print("=" * 60)
        print(f"Total Books:       {stats.total_books}")
        print(f"Total Categories:  {stats.total_categories}")
        print(f"Start Time:        {stats.start_time}")
        print(f"End Time:          {stats.end_time}")
        if stats.duration_seconds:
            print(f"Duration:          {stats.duration_seconds:.2f} seconds")
        print("=" * 60 + "\n")
    finally:
        await db_client.disconnect()


async def clear_database() -> None:
    """Clear all data from database."""
    await db_client.connect()
    try:
        response = input("Are you sure you want to clear all data? (yes/no): ")
        if response.lower() == "yes":
            count = await db_client.clear_all_books()
            print(f"Cleared {count} books from database")
        else:
            print("Operation cancelled")
    finally:
        await db_client.disconnect()


def start_api_server() -> None:
    """Start the FastAPI server."""
    import uvicorn

    logger.info("Starting API server...")
    uvicorn.run(
        "src.api:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        workers=settings.api_workers if not settings.api_reload else 1,
        log_level=settings.log_level.lower(),
    )


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Books to Scrape Crawler - Production Ready Web Scraping"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Crawl command
    crawl_parser = subparsers.add_parser("crawl", help="Start crawling")
    crawl_parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from checkpoint",
    )

    # Stats command
    subparsers.add_parser("stats", help="Show crawling statistics")

    # Clear command
    subparsers.add_parser("clear", help="Clear all data from database")

    # API command
    api_parser = subparsers.add_parser("api", help="Start API server")

    args = parser.parse_args()

    # Execute command
    try:
        if args.command == "crawl":
            asyncio.run(run_crawler(resume=args.resume))
        elif args.command == "stats":
            asyncio.run(show_stats())
        elif args.command == "clear":
            asyncio.run(clear_database())
        elif args.command == "api":
            start_api_server()
        else:
            parser.print_help()

    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
