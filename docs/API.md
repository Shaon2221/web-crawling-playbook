# API Documentation

## Authentication

All API endpoints (except root and health check) require authentication using an API key.

### API Key Header

```
X-API-Key: your-secret-api-key
```

### Obtaining API Keys

API keys are configured in the `.env` file:

```env
API_KEYS=key1,key2,key3
```

## Rate Limiting

API requests are rate-limited to prevent abuse:

- Default: 60 requests per minute per IP
- Configurable via `RATE_LIMIT_PER_MINUTE` environment variable

Rate limit headers in response:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1234567890
```

## Endpoints

### Root

**GET /**

Returns API information.

**Response:**
```json
{
  "name": "Books Crawler API",
  "version": "1.0.0",
  "documentation": "/docs"
}
```

### Health Check

**GET /health**

Check API and database health.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00.000000",
  "database": "connected",
  "scheduler": "running",
  "environment": "production"
}
```

### Get Books

**GET /api/v1/books**

Retrieve books with optional filtering and pagination.

**Authentication:** Required

**Query Parameters:**
- `skip` (integer): Number of records to skip (default: 0)
- `limit` (integer): Maximum records to return (default: 100, max: 100)
- `category` (string): Filter by category
- `min_price` (float): Minimum price filter
- `max_price` (float): Maximum price filter

**Example Request:**
```bash
curl -H "X-API-Key: your-key" \
  "http://localhost:8000/api/v1/books?category=Fiction&min_price=10&max_price=50&limit=20"
```

**Response:**
```json
{
  "books": [
    {
      "url": "https://books.toscrape.com/...",
      "title": "Book Title",
      "price": 25.99,
      "availability": "In stock",
      "rating": 4,
      "category": "Fiction",
      "upc": "abc123",
      "product_type": "Books",
      "price_excl_tax": 25.99,
      "price_incl_tax": 25.99,
      "tax": 0.00,
      "num_reviews": 10,
      "description": "Book description...",
      "image_url": "https://...",
      "first_scraped_at": "2024-01-01T00:00:00",
      "last_scraped_at": "2024-01-01T00:00:00",
      "scrape_count": 1,
      "price_history": []
    }
  ],
  "total": 100,
  "skip": 0,
  "limit": 20
}
```

### Get Statistics

**GET /api/v1/books/stats**

Get crawling statistics.

**Authentication:** Required

**Example Request:**
```bash
curl -H "X-API-Key: your-key" \
  "http://localhost:8000/api/v1/books/stats"
```

**Response:**
```json
{
  "total_books": 1000,
  "total_categories": 50,
  "total_pages": 0,
  "successful_requests": 0,
  "failed_requests": 0,
  "start_time": "2024-01-01T00:00:00",
  "end_time": "2024-01-01T01:00:00",
  "duration_seconds": 3600.5
}
```

### Start Crawl

**POST /api/v1/crawl/start**

Start a new crawl operation.

**Authentication:** Required

**Query Parameters:**
- `resume` (boolean): Resume from checkpoint (default: false)

**Example Request:**
```bash
curl -X POST -H "X-API-Key: your-key" \
  "http://localhost:8000/api/v1/crawl/start?resume=false"
```

**Response:**
```json
{
  "status": "started",
  "message": "Crawl started successfully",
  "started_at": "2024-01-01T00:00:00"
}
```

**Error Response (if crawl already running):**
```json
{
  "detail": "Crawl is already in progress",
  "timestamp": "2024-01-01T00:00:00"
}
```

### Get Crawl Status

**GET /api/v1/crawl/status**

Get current crawl operation status.

**Authentication:** Required

**Example Request:**
```bash
curl -H "X-API-Key: your-key" \
  "http://localhost:8000/api/v1/crawl/status"
```

**Response (Running):**
```json
{
  "status": "running",
  "message": "Crawl is currently in progress",
  "started_at": null
}
```

**Response (Completed):**
```json
{
  "status": "completed",
  "message": "Crawl completed successfully",
  "started_at": null
}
```

**Response (Not Started):**
```json
{
  "status": "not_started",
  "message": "No crawl has been started",
  "started_at": null
}
```

### Get Scheduler Jobs

**GET /api/v1/scheduler/jobs**

Get information about scheduled jobs.

**Authentication:** Required

**Example Request:**
```bash
curl -H "X-API-Key: your-key" \
  "http://localhost:8000/api/v1/scheduler/jobs"
```

**Response:**
```json
{
  "scheduler_enabled": true,
  "scheduler_running": true,
  "jobs": [
    {
      "id": "periodic_crawl",
      "name": "Periodic Crawl",
      "next_run_time": "2024-01-02T00:00:00"
    },
    {
      "id": "change_detection",
      "name": "Change Detection",
      "next_run_time": "2024-01-01T01:00:00"
    }
  ]
}
```

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message describing what went wrong",
  "timestamp": "2024-01-01T00:00:00.000000"
}
```

### Common HTTP Status Codes

- **200 OK**: Request successful
- **401 Unauthorized**: Missing or invalid API key
- **404 Not Found**: Resource not found
- **409 Conflict**: Resource conflict (e.g., crawl already running)
- **422 Unprocessable Entity**: Invalid request parameters
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Server error

## Interactive Documentation

FastAPI provides interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces allow you to:
- View all endpoints
- See request/response schemas
- Test API calls directly
- Download OpenAPI specification

## Code Examples

### Python

```python
import requests

API_KEY = "your-secret-api-key"
BASE_URL = "http://localhost:8000"

headers = {"X-API-Key": API_KEY}

# Get books
response = requests.get(
    f"{BASE_URL}/api/v1/books",
    headers=headers,
    params={"category": "Fiction", "limit": 10}
)
books = response.json()

# Start crawl
response = requests.post(
    f"{BASE_URL}/api/v1/crawl/start",
    headers=headers
)
result = response.json()
```

### JavaScript

```javascript
const API_KEY = 'your-secret-api-key';
const BASE_URL = 'http://localhost:8000';

const headers = {
  'X-API-Key': API_KEY
};

// Get books
fetch(`${BASE_URL}/api/v1/books?category=Fiction&limit=10`, {
  headers: headers
})
  .then(response => response.json())
  .then(data => console.log(data));

// Start crawl
fetch(`${BASE_URL}/api/v1/crawl/start`, {
  method: 'POST',
  headers: headers
})
  .then(response => response.json())
  .then(data => console.log(data));
```

### cURL

```bash
# Set API key
export API_KEY="your-secret-api-key"

# Get books
curl -H "X-API-Key: $API_KEY" \
  "http://localhost:8000/api/v1/books?category=Fiction&limit=10"

# Start crawl
curl -X POST -H "X-API-Key: $API_KEY" \
  "http://localhost:8000/api/v1/crawl/start"

# Get statistics
curl -H "X-API-Key: $API_KEY" \
  "http://localhost:8000/api/v1/books/stats"
```

## WebSocket Support

Currently not implemented. Future enhancement for real-time crawl updates.

## Versioning

API versioning is included in the URL path (`/api/v1/`). Future versions will use `/api/v2/`, etc.

## Deprecation Policy

- Deprecated endpoints will be marked 6 months before removal
- Version support: Current + 1 previous version
- Breaking changes only in major versions
