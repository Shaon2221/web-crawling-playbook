# Books-to-Scrape Web Crawler: Complete Production-Ready Playbook

A comprehensive, production-ready web scraping solution for the Books to Scrape website, built with Python 3.11+, featuring async crawling, MongoDB storage, REST API, scheduling, and full CI/CD pipeline.

## 🚀 Features

- **Async Web Crawler**: High-performance async crawler with configurable concurrency
- **Retry & Resume**: Automatic retry with exponential backoff and checkpoint-based resume
- **MongoDB Integration**: Structured data storage with change detection and price history
- **REST API**: FastAPI-powered API with Swagger documentation
- **API Security**: API key authentication and rate limiting
- **Scheduler**: Automated periodic crawling and change detection
- **Comprehensive Logging**: Structured logging with rotation
- **Docker Support**: Full containerization with docker-compose
- **CI/CD Pipeline**: GitHub Actions workflow for testing and deployment
- **Production Ready**: Error handling, health checks, monitoring

## 📁 Project Structure

```
books-crawler/
├── src/
│   ├── __init__.py
│   ├── __main__.py          # CLI entry point
│   ├── config.py            # Configuration management
│   ├── api/
│   │   ├── __init__.py      # FastAPI application
│   │   ├── models.py        # API response models
│   │   └── security.py      # Authentication & authorization
│   ├── crawler/
│   │   ├── __init__.py      # Main crawler logic
│   │   ├── parser.py        # HTML parsing utilities
│   │   └── checkpoint.py    # Resume/checkpoint manager
│   ├── database/
│   │   ├── __init__.py      # MongoDB client
│   │   └── models.py        # Data models
│   ├── scheduler/
│   │   └── __init__.py      # APScheduler integration
│   └── utils/
│       └── __init__.py      # Logging utilities
├── tests/
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   └── conftest.py          # Pytest configuration
├── docs/                    # Documentation
├── data/
│   ├── sample/              # Sample data
│   └── checkpoints/         # Crawler checkpoints
├── scripts/                 # Utility scripts
├── .github/
│   └── workflows/
│       └── ci.yml           # GitHub Actions CI/CD
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker Compose setup
├── pyproject.toml           # Project metadata
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variables template
├── .gitignore
├── .dockerignore
└── README.md
```

## 🔧 Installation

### Prerequisites

- Python 3.11 or higher
- MongoDB 7.0 or higher
- Docker & Docker Compose (optional)

### Local Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/books-crawler.git
   cd books-crawler
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Start MongoDB**:
   ```bash
   # Using Docker
   docker run -d -p 27017:27017 --name mongodb mongo:7.0

   # Or use your local MongoDB installation
   ```

### Docker Setup

1. **Copy environment file**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

2. **Start all services**:
   ```bash
   docker-compose up -d
   ```

3. **View logs**:
   ```bash
   docker-compose logs -f crawler-api
   ```

## 🎯 Usage

### Command Line Interface

The crawler provides a CLI for various operations:

```bash
# Start a full crawl
python -m src crawl

# Resume from checkpoint
python -m src crawl --resume

# View statistics
python -m src stats

# Start API server
python -m src api

# Clear database
python -m src clear
```

### REST API

Start the API server:
```bash
python -m src api
```

The API will be available at `http://localhost:8000`

#### API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

#### Authentication

All API endpoints (except `/` and `/health`) require an API key:

```bash
curl -H "X-API-Key: your-secret-api-key" http://localhost:8000/api/v1/books
```

#### Main Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/health` | GET | Health check |
| `/api/v1/books` | GET | Get books (with filters) |
| `/api/v1/books/stats` | GET | Get crawl statistics |
| `/api/v1/crawl/start` | POST | Start crawl |
| `/api/v1/crawl/status` | GET | Get crawl status |
| `/api/v1/scheduler/jobs` | GET | Get scheduled jobs |

#### Example Requests

**Get all books**:
```bash
curl -H "X-API-Key: your-api-key" \
  "http://localhost:8000/api/v1/books?limit=10"
```

**Filter by category and price**:
```bash
curl -H "X-API-Key: your-api-key" \
  "http://localhost:8000/api/v1/books?category=Fiction&min_price=10&max_price=50"
```

**Get statistics**:
```bash
curl -H "X-API-Key: your-api-key" \
  "http://localhost:8000/api/v1/books/stats"
```

**Start crawl**:
```bash
curl -X POST -H "X-API-Key: your-api-key" \
  "http://localhost:8000/api/v1/crawl/start"
```

### Python API

Use the crawler programmatically:

```python
import asyncio
from src.crawler import BooksCrawler

async def main():
    async with BooksCrawler() as crawler:
        await crawler.crawl_all()

asyncio.run(main())
```

## ⚙️ Configuration

Configuration is managed through environment variables. See `.env.example` for all options:

### Key Settings

- **MongoDB**: `MONGODB_URL`, `MONGODB_DB_NAME`
- **Crawler**: `CRAWLER_MAX_CONCURRENT_REQUESTS`, `CRAWLER_REQUEST_DELAY`
- **API**: `API_HOST`, `API_PORT`, `API_KEYS`
- **Rate Limit**: `RATE_LIMIT_PER_MINUTE`
- **Scheduler**: `SCHEDULER_ENABLED`, `SCHEDULER_INTERVAL_HOURS`
- **Logging**: `LOG_LEVEL`, `LOG_FILE`

## 🧪 Testing

Run tests with pytest:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test suite
pytest tests/unit/
pytest tests/integration/

# Run with verbose output
pytest -v
```

## 🐳 Docker Deployment

### Build and Run

```bash
# Build image
docker build -t books-crawler .

# Run with docker-compose
docker-compose up -d

# Scale workers
docker-compose up -d --scale crawler-worker=3

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Docker Services

- **mongodb**: MongoDB database
- **crawler-api**: FastAPI REST API
- **crawler-worker**: Background crawler (optional)
- **mongo-express**: MongoDB UI (dev profile)

## 📊 MongoDB Schema

### Books Collection

```javascript
{
  "_id": ObjectId,
  "url": String,              // Unique book URL
  "title": String,
  "price": Number,
  "availability": String,
  "rating": Number,           // 0-5
  "category": String,
  "upc": String,
  "product_type": String,
  "price_excl_tax": Number,
  "price_incl_tax": Number,
  "tax": Number,
  "num_reviews": Number,
  "description": String,
  "image_url": String,
  "first_scraped_at": Date,
  "last_scraped_at": Date,
  "scrape_count": Number,
  "price_history": [
    {
      "price": Number,
      "changed_at": Date
    }
  ]
}
```

### Indexes

- `url`: Unique index
- `category`: For category filtering
- `price`: For price range queries
- `last_scraped_at`: For sorting by recency

## 📈 Monitoring & Logging

### Logging

Logs are written to both console and file (`logs/crawler.log`):

```python
# Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO
LOG_FILE=logs/crawler.log
```

### Health Checks

Check application health:
```bash
curl http://localhost:8000/health
```

Returns:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00",
  "database": "connected",
  "scheduler": "running",
  "environment": "production"
}
```

## 🔄 CI/CD Pipeline

GitHub Actions workflow (`.github/workflows/ci.yml`):

1. **Linting**: Ruff for code quality
2. **Type Checking**: MyPy for type safety
3. **Testing**: Pytest with coverage
4. **Docker Build**: Multi-stage build
5. **Security Scan**: Trivy vulnerability scanner

### Triggering CI/CD

```bash
# Push to main/develop branch
git push origin main

# Create pull request
gh pr create --base main --head feature-branch
```

## 🔒 Security

### API Key Management

- Generate strong API keys
- Store keys in environment variables
- Use different keys for different environments
- Rotate keys regularly

### Rate Limiting

Configure rate limits in `.env`:
```
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
```

### Best Practices

- Never commit `.env` files
- Use Docker secrets in production
- Enable HTTPS in production
- Regular security updates

## 🚦 Development Workflow

1. **Create feature branch**:
   ```bash
   git checkout -b feature/new-feature
   ```

2. **Make changes and test**:
   ```bash
   pytest
   ruff check src/
   ```

3. **Commit changes**:
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

4. **Push and create PR**:
   ```bash
   git push origin feature/new-feature
   gh pr create
   ```

## 📚 Additional Resources

- [Books to Scrape](https://books.toscrape.com/) - Target website
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Motor Documentation](https://motor.readthedocs.io/)
- [aiohttp Documentation](https://docs.aiohttp.org/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 👥 Support

For issues and questions:
- GitHub Issues: https://github.com/yourusername/books-crawler/issues
- Email: support@example.com

## 🎉 Acknowledgments

- Books to Scrape for providing the test website
- FastAPI and Pydantic teams
- MongoDB team
- All contributors

---

**Made with ❤️ for the web scraping community**
