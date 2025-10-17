"""FastAPI application with endpoints for book crawling."""

import asyncio
from datetime import datetime
from typing import Optional, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from src.config import settings
from src.database import db_client
from src.database.models import BookModel
from src.crawler import BooksCrawler
from src.scheduler import scheduler
from src.api.security import verify_api_key
from src.api.models import (
    BooksListResponse,
    BookResponse,
    StatsResponse,
    CrawlResponse,
    HealthResponse,
    ErrorResponse,
)
from src.utils import logger


# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# Background crawler task
crawler_task: Optional[asyncio.Task] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting application...")
    await db_client.connect()

    # Start scheduler if enabled
    if settings.scheduler_enabled:
        scheduler.start()

    logger.info("Application started successfully")

    yield

    # Shutdown
    logger.info("Shutting down application...")

    # Cancel any running crawler task
    if crawler_task and not crawler_task.done():
        crawler_task.cancel()
        try:
            await crawler_task
        except asyncio.CancelledError:
            pass

    # Stop scheduler
    if settings.scheduler_enabled:
        scheduler.stop()

    await db_client.disconnect()
    logger.info("Application shut down successfully")


# Create FastAPI app
app = FastAPI(
    title="Books Crawler API",
    description="Production-ready API for Books to Scrape web crawler",
    version="1.0.0",
    lifespan=lifespan,
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
async def root() -> dict:
    """Root endpoint."""
    return {
        "name": "Books Crawler API",
        "version": "1.0.0",
        "documentation": "/docs",
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    # Check database connection
    db_status = "connected"
    try:
        if db_client.collection:
            await db_client.collection.find_one()
    except Exception as e:
        db_status = f"error: {str(e)}"
        logger.error(f"Database health check failed: {e}")

    # Check scheduler status
    scheduler_status = "running" if scheduler.scheduler.running else "stopped"

    return HealthResponse(
        status="healthy" if db_status == "connected" else "degraded",
        timestamp=datetime.utcnow(),
        database=db_status,
        scheduler=scheduler_status,
        environment=settings.environment,
    )


@app.get(
    "/api/v1/books",
    response_model=BooksListResponse,
    tags=["Books"],
    dependencies=[Depends(verify_api_key)],
)
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def get_books(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
) -> BooksListResponse:
    """
    Get books with optional filtering and pagination.

    Args:
        skip: Number of books to skip
        limit: Maximum number of books to return (max 100)
        category: Filter by category
        min_price: Minimum price filter
        max_price: Maximum price filter

    Returns:
        List of books with pagination info
    """
    # Validate limit
    if limit > 100:
        limit = 100

    try:
        books = await db_client.get_books(
            skip=skip,
            limit=limit,
            category=category,
            min_price=min_price,
            max_price=max_price,
        )

        # Get total count
        query = {}
        if category:
            query["category"] = category
        if min_price is not None or max_price is not None:
            query["price"] = {}
            if min_price is not None:
                query["price"]["$gte"] = min_price
            if max_price is not None:
                query["price"]["$lte"] = max_price

        total = await db_client.collection.count_documents(query) if db_client.collection else 0

        # Convert to response models
        book_responses = [BookResponse(**book) for book in books]

        return BooksListResponse(
            books=book_responses,
            total=total,
            skip=skip,
            limit=limit,
        )

    except Exception as e:
        logger.error(f"Error fetching books: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching books: {str(e)}",
        )


@app.get(
    "/api/v1/books/stats",
    response_model=StatsResponse,
    tags=["Books"],
    dependencies=[Depends(verify_api_key)],
)
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def get_stats(request: Request) -> StatsResponse:
    """Get crawling statistics."""
    try:
        stats = await db_client.get_stats()
        return StatsResponse(**stats.model_dump())
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching stats: {str(e)}",
        )


@app.post(
    "/api/v1/crawl/start",
    response_model=CrawlResponse,
    tags=["Crawler"],
    dependencies=[Depends(verify_api_key)],
)
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def start_crawl(request: Request, resume: bool = False) -> CrawlResponse:
    """
    Start a new crawl operation.

    Args:
        resume: Resume from checkpoint if available

    Returns:
        Crawl operation status
    """
    global crawler_task

    # Check if crawl is already running
    if crawler_task and not crawler_task.done():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Crawl is already in progress",
        )

    async def run_crawler():
        """Background task to run crawler."""
        try:
            async with BooksCrawler() as crawler:
                if resume:
                    await crawler.resume_crawl()
                else:
                    await crawler.crawl_all()
        except Exception as e:
            logger.error(f"Crawler error: {e}")

    # Start crawler in background
    crawler_task = asyncio.create_task(run_crawler())
    started_at = datetime.utcnow()

    logger.info(f"Crawl started (resume={resume})")

    return CrawlResponse(
        status="started",
        message=f"Crawl {'resumed' if resume else 'started'} successfully",
        started_at=started_at,
    )


@app.get(
    "/api/v1/crawl/status",
    response_model=CrawlResponse,
    tags=["Crawler"],
    dependencies=[Depends(verify_api_key)],
)
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def get_crawl_status(request: Request) -> CrawlResponse:
    """Get current crawl status."""
    global crawler_task

    if crawler_task is None:
        return CrawlResponse(
            status="not_started",
            message="No crawl has been started",
        )

    if crawler_task.done():
        # Check if task completed successfully or with error
        try:
            crawler_task.result()
            return CrawlResponse(
                status="completed",
                message="Crawl completed successfully",
            )
        except Exception as e:
            return CrawlResponse(
                status="failed",
                message=f"Crawl failed: {str(e)}",
            )
    else:
        return CrawlResponse(
            status="running",
            message="Crawl is currently in progress",
        )


@app.get(
    "/api/v1/scheduler/jobs",
    tags=["Scheduler"],
    dependencies=[Depends(verify_api_key)],
)
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def get_scheduler_jobs(request: Request) -> dict:
    """Get scheduled jobs information."""
    jobs = scheduler.get_jobs()
    jobs_info = []

    for job in jobs:
        jobs_info.append(
            {
                "id": job.id,
                "name": job.name,
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
            }
        )

    return {
        "scheduler_enabled": settings.scheduler_enabled,
        "scheduler_running": scheduler.scheduler.running,
        "jobs": jobs_info,
    }


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(detail=exc.detail).model_dump(),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(detail="Internal server error").model_dump(),
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.api:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        log_level=settings.log_level.lower(),
    )
