# Books-to-Scrape: Production-Grade Web Crawler

> A production-ready web crawler for [books.toscrape.com](https://books.toscrape.com) with async HTTP, MongoDB persistence, daily change detection, and secure REST API.

**Status:** ✅ Production Ready | **Test Coverage:** 80%+ | **Python:** 3.11+ | **License:** MIT

## ⚡ Quick Start

```bash
# Clone & start services (5 min)
git clone https://github.com/Shaon2221/web-crawling-playbook.git
cd web-crawling-playbook

# Start with Docker (all services)
docker-compose up -d
sleep 30

# Run crawler (10 min)
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python scripts/run_crawler.py

# Test API
curl -H "X-API-Key: test-key-123" http://localhost:8000/api/v1/books
open http://localhost:8000/docs  # Swagger UI
```

---

## ✨ Features

- ✅ **Async Web Crawler** — Fast concurrent scraping with exponential backoff retry logic
- ✅ **Resumable Crawling** — Checkpoint-based recovery after failures
- ✅ **Change Detection** — Daily scheduled crawls with automatic change tracking
- ✅ **REST API** — FastAPI with API key authentication and rate limiting
- ✅ **MongoDB Persistence** — Efficient storage with indexed queries
- ✅ **Structured Logging** — JSON-formatted logs for easy parsing and monitoring
- ✅ **Email Alerts** — Notifications on detected changes
- ✅ **High Test Coverage** — Comprehensive pytest suite
- ✅ **Docker Compose** — Complete local dev environment with all services
- ✅ **CI/CD Pipeline** — GitHub Actions for automated testing and builds

## 📋 Requirements

- **Python 3.11+** or **Python 3.12** (tested)
- **MongoDB 5.0+** (local or Atlas)
- **Redis 6.0+** (for rate limiting)
- **Docker & Docker Compose** (recommended for easy setup)

---

## 🔧 Setup & Configuration

### Prerequisites
- **Python 3.11+** or **3.12** (tested)
- **Docker & Docker Compose** (recommended)
- **MongoDB 5.0+** or use Docker
- **Redis 6.0+** or use Docker
- ~5GB disk space

### Environment Variables

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Key variables:
```bash
# MongoDB
MONGO_URI=mongodb://localhost:27017
MONGO_DB=books_scraper

# Crawler
CRAWLER_TIMEOUT=30
CRAWLER_MAX_RETRIES=3
CRAWLER_BACKOFF_FACTOR=2.0

# API
API_HOST=0.0.0.0
API_PORT=8000
VALID_API_KEYS=test-key-123,test-key-456

# Rate Limiting
RATE_LIMIT_REQUESTS=100
REDIS_URL=redis://localhost:6379

# Logging
LOG_LEVEL=INFO

# Alerts (optional)
ALERT_EMAIL_ENABLED=false
```

---

## 📚 Local Development (Without Docker)

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start MongoDB & Redis (use Docker for these)
docker run -d -p 27017:27017 --name mongo mongo:6.0
docker run -d -p 6379:6379 --name redis redis:7-alpine

# Run crawler (Terminal 1)
python scripts/run_crawler.py

# Start API server (Terminal 2)
uvicorn src.api.main:app --reload --port 8000

# Start scheduler (Terminal 3)
python scripts/run_scheduler.py
```

---

## � API Reference

### Authentication
All endpoints (except `/health`) require: `X-API-Key: your-api-key-here` header

### Endpoints

**GET /api/v1/books** — Get books with filters
```bash
curl -H "X-API-Key: test-key-123" \
  "http://localhost:8000/api/v1/books?category=Fiction&min_price=10&max_price=50&sort_by=rating&page=1&limit=10"
```
Parameters: `category`, `min_price`, `max_price`, `rating`, `sort_by` (name/price/rating/reviews), `page`, `limit`

**GET /api/v1/books/{book_id}** — Get single book
```bash
curl -H "X-API-Key: test-key-123" http://localhost:8000/api/v1/books/507f1f77bcf86cd799439011
```

**GET /api/v1/changes** — Get recent changes
```bash
curl -H "X-API-Key: test-key-123" \
  "http://localhost:8000/api/v1/changes?hours=24&page=1&limit=10"
```
Parameters: `hours` (1-720), `page`, `limit`

**GET /health** — Health check (no auth)
```bash
curl http://localhost:8000/health
```

### Response Example (GET /api/v1/books)
```json
[
  {
    "id": "507f1f77bcf86cd799439011",
    "name": "A Light in the Attic",
    "category": "Poetry",
    "price_incl_tax": 51.77,
    "price_excl_tax": 51.77,
    "availability": "In stock (22 available)",
    "num_reviews": 0,
    "rating": 3.0,
    "image_url": "https://books.toscrape.com/media/cache/...",
    "status": "active",
    "crawled_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00"
  }
]
```

### Interactive Testing
- **Swagger UI:** Open **http://localhost:8000/docs** in browser for live API testing
- **Postman Collection:** Import `postman_collection.json` into Postman with 15+ pre-configured requests
  ```bash
  # Quick import: paste file URL or drag-drop postman_collection.json into Postman
  ```

---

## 🧪 Testing

```bash
# Run all tests
pytest -v

# With coverage
pytest --cov=src --cov-fail-under=80

# View coverage report
open htmlcov/index.html
```

**Results:** 25+ tests, 80%+ coverage ✅

## 📁 Project Structure

```
web-crawling-playbook/
├── src/                           # Application code
│   ├── crawler/                   # Web crawling
│   │   ├── client.py             # Async HTTP with retries
│   │   ├── parser.py             # BeautifulSoup extraction
│   │   ├── checkpoint.py         # Resumable crawling
│   │   └── storage.py            # MongoDB persistence
│   ├── scheduler/                 # Daily jobs
│   │   ├── tasks.py              # APScheduler setup
│   │   ├── change_detector.py    # Change detection
│   │   └── alerts.py             # Email alerts
│   ├── api/                       # REST API
│   │   ├── main.py               # FastAPI app & endpoints
│   │   ├── auth.py               # API key validation
│   │   └── middleware.py         # Rate limiting & auth
│   ├── models/book.py            # Pydantic schemas
│   ├── db/mongo.py               # MongoDB manager
│   ├── config.py                 # Configuration
│   └── logger.py                 # JSON logging
├── tests/                         # Test suite (80%+ coverage)
│   ├── conftest.py
│   ├── test_parser.py
│   └── test_api.py
├── scripts/                       # CLI entry points
│   ├── run_crawler.py            # One-time crawl
│   ├── run_scheduler.py          # Daily scheduler
│   └── init_db.py                # Initialize DB
├── docker-compose.yml            # Multi-service setup
├── Dockerfile                    # API image
├── Dockerfile.scheduler          # Scheduler image
├── requirements.txt              # Dependencies
├── .env.example                  # Config template
└── README.md                     # This file
```

## � Authentication & Authorization

- **API Key Authentication:** All endpoints require `X-API-Key` header (except `/health`)
- **Rate Limiting:** 100 requests per hour per API key (configurable)
- **Validation:** Pydantic schemas validate all inputs
- **Error Handling:** 401 (missing key), 403 (invalid key), 429 (rate limit)

### Database Schema (MongoDB)

**books** collection
```json
{
  "url": "unique, indexed",
  "name": "book title",
  "category": "indexed",
  "price_incl_tax": "indexed for range queries",
  "rating": "indexed (descending)",
  "availability": "in stock status",
  "num_reviews": "review count",
  "description": "full text searchable",
  "image_url": "book cover",
  "raw_html": "full HTML snapshot",
  "content_hash": "SHA256 for change detection",
  "status": "active|unavailable|removed",
  "crawled_at": "timestamp",
  "updated_at": "timestamp"
}
```

**changes** collection tracks: price changes, availability changes, new books
**crawler_checkpoints** collection stores: resumable crawl state (last_page, status)

## �️ Troubleshooting & FAQ

| Issue | Solution |
|-------|----------|
| **Docker won't start** | Check: `docker ps`, `docker-compose logs` |
| **MongoDB connection error** | Verify MONGO_URI in .env, test with: `curl http://localhost:8000/health` |
| **API returns empty results** | Run crawler first: `python scripts/run_crawler.py` |
| **Rate limit exceeded** | Default: 100/hr. Wait 1 hour or increase in .env: `RATE_LIMIT_REQUESTS=1000` |
| **Tests failing** | Ensure services running: `docker-compose ps`, then: `pytest -v -s` |
| **Permission denied** | Make executable: `chmod +x scripts/run_crawler.py` |
| **Crawler timeout** | Increase in .env: `CRAWLER_TIMEOUT=60`, or check site connectivity |

## 🚀 Production Deployment

### Docker Setup (Recommended)
```bash
# 1. Update .env for production
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/books_scraper
VALID_API_KEYS=<strong-random-key>
LOG_LEVEL=WARNING

# 2. Build and deploy
docker-compose -f docker-compose.yml up -d

# 3. Set up reverse proxy (Nginx with SSL recommended)
# 4. Monitor with: docker-compose logs -f api
```

### Key Production Settings
- Enable email alerts: `ALERT_EMAIL_ENABLED=true`
- Reduce log level: `LOG_LEVEL=WARNING`
- Use strong API keys (rotate quarterly)
- Enable MongoDB authentication
- Use Redis password
- Set up SSL/HTTPS
- Configure CloudWatch or monitoring service
- Enable automated backups

---

## ✨ Features Implemented

✅ **Crawler**
- Async HTTP with exponential backoff retries
- Resumable from checkpoints
- Connection pooling (10 concurrent)
- Content hashing for change detection
- Pydantic model validation

✅ **Scheduler**
- APScheduler with asyncio
- Daily execution (2 AM UTC, configurable)
- Automatic change detection
- Email alerting on changes
- JSON structured logging

✅ **API**
- FastAPI with OpenAPI/Swagger
- 3 RESTful endpoints
- Filtering, sorting, pagination
- X-API-Key authentication
- Redis-backed rate limiting
- CORS support

✅ **Database**
- MongoDB with optimized indices
- 3 collections (books, changes, checkpoints)
- Async Motor driver
- Connection pooling

✅ **Testing**
- 25+ unit/integration tests
- 80%+ code coverage
- pytest with async support
- CI/CD with GitHub Actions

---

## 📊 Performance

| Metric | Value |
|--------|-------|
| Crawl speed | 500-1000 books/min |
| API response | <100ms avg |
| Memory usage | ~150MB |
| Docker image | ~450MB |
| Test coverage | 80%+ |
| Connection pool | 10 concurrent |
| Rate limit | 100 req/hr per key |

---

## 🔗 Code Locations (FAQ)

**Where is X-API-Key authentication?**
- `src/api/auth.py` — `verify_api_key()` function
- `src/api/middleware.py` — `APIKeyMiddleware` class
- `.env` — `VALID_API_KEYS` variable

**Where is MongoDB setup?**
- `src/db/mongo.py` — `MongoDBManager` class
- `src/crawler/storage.py` — Data persistence
- `.env` — `MONGO_URI` and `MONGO_DB` variables
- Collections: `books`, `changes`, `crawler_checkpoints`

**Where is scraped data stored?**
- **Database:** MongoDB `books_scraper.books` collection
- **Fields:** name, category, price_incl_tax, availability, rating, image_url, raw_html, content_hash, etc.
- **Query:** `db.books.find()` or use `/api/v1/books` endpoint

**Where are logs?**
- `logs/app.log` — API logs
- `logs/crawler.log` — Crawler logs
- `logs/scheduler.log` — Scheduler logs
- Format: JSON with timestamp, level, logger, message

**Where is change detection?**
- `src/scheduler/change_detector.py` — Detection logic
- MongoDB `changes` collection — Change log
- Tracks: price, availability, new books
- `/api/v1/changes` endpoint — Query recent changes

---

## 📚 Technologies Used

| Component | Technology | Why? |
|-----------|-----------|------|
| **Language** | Python 3.11+ | Modern async support |
| **HTTP** | httpx | Async, modern, better retry API |
| **Parsing** | BeautifulSoup4 + lxml | Robust HTML extraction |
| **Database** | MongoDB | NoSQL, flexible schema, performant |
| **Async Driver** | Motor | Native async MongoDB |
| **Framework** | FastAPI | Modern, fast, auto-OpenAPI |
| **Scheduling** | APScheduler | Flexible cron with async |
| **Auth** | API Key | Simple, effective, configurable |
| **Cache/Rate** | Redis + Middleware | Distributed, stateless |
| **Testing** | pytest + pytest-asyncio | Industry standard async support |
| **Containers** | Docker Compose | Multi-service orchestration |

---

## 📖 For More Information

- **API Examples:** See above API Reference section
- **Advanced Topics:** Check inline code comments
- **GitHub:** https://github.com/Shaon2221/web-crawling-playbook
- **Issues:** File issues on GitHub repo

---

## 📝 License

MIT

## ✅ Status

✅ **Production Ready** | ✅ **80%+ Test Coverage** | ✅ **Fully Documented** | ✅ **Docker Ready**

**Questions?** Check the API Reference or code comments. Happy scraping! 🚀

