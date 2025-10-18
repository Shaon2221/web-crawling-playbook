"""FastAPI main application with MongoDB lifespan events."""

from contextlib import asynccontextmanager
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query

from src.api.auth import verify_api_key
from src.api.middleware import APIKeyMiddleware, RateLimitMiddleware
from src.config import settings
from src.db.mongo import MongoDBManager
from src.logger import api_logger
from src.models.book import BookResponse

# Global MongoDB instance
db_manager: Optional[MongoDBManager] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events: startup and shutdown."""
    global db_manager

    # Startup
    api_logger.info("🚀 Starting FastAPI application")
    db_manager = MongoDBManager(settings.mongo_uri, settings.mongo_db)
    await db_manager.connect()
    api_logger.info("✅ Database connected")

    yield

    # Shutdown
    api_logger.info("⏹️ Shutting down FastAPI application")
    await db_manager.disconnect()


# Create FastAPI app
app = FastAPI(
    title="Books Scraper API",
    version="1.0.0",
    description="RESTful API for books.toscrape.com crawler with change detection",
    lifespan=lifespan,
)

# Add middleware
app.add_middleware(RateLimitMiddleware)
app.add_middleware(APIKeyMiddleware)


@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    """
    Health check endpoint (no authentication required).

    Returns:
        Health status
    """
    is_healthy = await db_manager.health_check()
    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "database": "connected" if is_healthy else "disconnected",
    }


@app.get("/api/v1/books", response_model=list[BookResponse], tags=["Books"])
async def get_books(
    category: Optional[str] = Query(None, description="Filter by category"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    rating: Optional[float] = Query(None, ge=0, le=5, description="Minimum rating"),
    sort_by: Optional[str] = Query(
        "name",
        regex="^(name|price|rating|reviews)$",
        description="Sort field",
    ),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    api_key: str = Depends(verify_api_key),
) -> list[dict]:
    """
    Get books with filtering, sorting, and pagination.

    Query Parameters:
    - category: Filter by book category
    - min_price, max_price: Filter by price range
    - rating: Filter by minimum rating
    - sort_by: Sort field (name, price, rating, reviews)
    - page: Page number (1-indexed)
    - limit: Items per page (max 100)

    Returns:
        List of books
    """
    try:
        collection = db_manager.db["books"]

        # Build query filter
        filter_query = {}

        if category:
            filter_query["category"] = category

        if min_price is not None or max_price is not None:
            price_query = {}
            if min_price is not None:
                price_query["$gte"] = min_price
            if max_price is not None:
                price_query["$lte"] = max_price
            filter_query["price_incl_tax"] = price_query

        if rating is not None:
            filter_query["rating"] = {"$gte": rating}

        # Sorting
        sort_map = {
            "name": ("name", 1),
            "price": ("price_incl_tax", 1),
            "rating": ("rating", -1),
            "reviews": ("num_reviews", -1),
        }
        sort_field, sort_order = sort_map.get(sort_by, ("name", 1))

        # Pagination
        skip = (page - 1) * limit

        # Execute query
        cursor = collection.find(filter_query).sort(sort_field, sort_order).skip(skip).limit(limit)
        books = await cursor.to_list(length=limit)

        # Convert to response models
        responses = [BookResponse(**{**book, "_id": str(book["_id"])}) for book in books]

        api_logger.info(f"✅ GET /books: returned {len(responses)} books (page {page})")
        return responses

    except Exception as e:
        api_logger.error(f"❌ Error fetching books: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/v1/books/{book_id}", response_model=BookResponse, tags=["Books"])
async def get_book_by_id(
    book_id: str,
    api_key: str = Depends(verify_api_key),
) -> dict:
    """
    Get single book by ID.

    Args:
        book_id: MongoDB ObjectId

    Returns:
        Book details
    """
    try:
        from bson import ObjectId

        collection = db_manager.db["books"]
        try:
            book = await collection.find_one({"_id": ObjectId(book_id)})
        except Exception:
            book = await collection.find_one({"_id": book_id})

        if not book:
            raise HTTPException(status_code=404, detail="Book not found")

        api_logger.info(f"✅ GET /books/{book_id}")
        return BookResponse(**{**book, "_id": str(book["_id"])})

    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"❌ Error fetching book {book_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/v1/changes", response_model=list[dict], tags=["Changes"])
async def get_recent_changes(
    hours: int = Query(24, ge=1, le=720, description="Look back N hours"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    api_key: str = Depends(verify_api_key),
) -> list[dict]:
    """
    Get recent changes detected by the scheduler.

    Query Parameters:
    - hours: Look back N hours (default 24)
    - page: Page number
    - limit: Items per page

    Returns:
        List of detected changes
    """
    try:
        from datetime import datetime, timedelta

        changes_collection = db_manager.db["changes"]
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        # Query
        skip = (page - 1) * limit
        cursor = (
            changes_collection.find(
                {"detected_at": {"$gte": cutoff_time}},
                sort=[("detected_at", -1)],
            )
            .skip(skip)
            .limit(limit)
        )

        changes = await cursor.to_list(length=limit)

        # Convert ObjectIds to strings
        for change in changes:
            change["_id"] = str(change["_id"])
            change["book_id"] = str(change["book_id"])
            change["detected_at"] = change["detected_at"].isoformat()

        api_logger.info(f"✅ GET /changes: returned {len(changes)} changes")
        return changes

    except Exception as e:
        api_logger.error(f"❌ Error fetching changes: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
