# Quick Reference Guide

## Common Commands

### CLI Operations

```bash
# Start full crawl
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

### Make Commands

```bash
# Install dependencies
make install

# Run tests
make test
make test-cov

# Linting and formatting
make lint
make format

# Run application
make run-api
make run-crawler

# Docker operations
make docker-build
make docker-up
make docker-down
make docker-logs
```

### Docker Commands

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f crawler-api

# Stop services
docker-compose down

# Restart a service
docker-compose restart crawler-api

# Scale workers
docker-compose up -d --scale crawler-worker=3

# Execute command in container
docker-compose exec crawler-api python -m src stats
```

## API Endpoints

### Public Endpoints

```bash
# Root
curl http://localhost:8000/

# Health check
curl http://localhost:8000/health
```

### Protected Endpoints (require API key)

```bash
# Set API key
export API_KEY="your-api-key"

# Get all books
curl -H "X-API-Key: $API_KEY" \
  http://localhost:8000/api/v1/books

# Get books with filters
curl -H "X-API-Key: $API_KEY" \
  "http://localhost:8000/api/v1/books?category=Fiction&min_price=10&max_price=50&limit=20"

# Get statistics
curl -H "X-API-Key: $API_KEY" \
  http://localhost:8000/api/v1/books/stats

# Start crawl
curl -X POST -H "X-API-Key: $API_KEY" \
  http://localhost:8000/api/v1/crawl/start

# Get crawl status
curl -H "X-API-Key: $API_KEY" \
  http://localhost:8000/api/v1/crawl/status

# Get scheduler jobs
curl -H "X-API-Key: $API_KEY" \
  http://localhost:8000/api/v1/scheduler/jobs
```

## Configuration Quick Reference

### Essential Environment Variables

```env
# MongoDB
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=books_crawler

# Crawler
CRAWLER_MAX_CONCURRENT_REQUESTS=10
CRAWLER_REQUEST_DELAY=0.5
CRAWLER_MAX_RETRIES=3

# API
API_HOST=0.0.0.0
API_PORT=8000
API_KEYS=your-secret-key-1,your-secret-key-2

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60

# Scheduler
SCHEDULER_ENABLED=true
SCHEDULER_INTERVAL_HOURS=24

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/crawler.log
```

## MongoDB Queries

### Useful MongoDB Queries

```javascript
// Connect to database
mongosh mongodb://localhost:27017/books_crawler

// Count total books
db.books.countDocuments()

// Find books by category
db.books.find({ category: "Fiction" })

// Find books in price range
db.books.find({ price: { $gte: 10, $lte: 50 } })

// Books with price changes
db.books.find({ "price_history.0": { $exists: true } })

// Most expensive books
db.books.find().sort({ price: -1 }).limit(10)

// Recently scraped books
db.books.find().sort({ last_scraped_at: -1 }).limit(10)

// Books by rating
db.books.find({ rating: 5 })

// Categories with book count
db.books.aggregate([
  { $group: { _id: "$category", count: { $sum: 1 } } },
  { $sort: { count: -1 } }
])

// Average price by category
db.books.aggregate([
  { $group: { _id: "$category", avg_price: { $avg: "$price" } } }
])
```

## Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Find process using port 8000
lsof -i :8000
# or
netstat -tulpn | grep 8000

# Kill process
kill -9 <PID>
```

**MongoDB connection failed:**
```bash
# Check if MongoDB is running
docker ps | grep mongodb

# Start MongoDB
docker start mongodb
# or
docker run -d -p 27017:27017 --name mongodb mongo:7.0
```

**Crawler hanging:**
```bash
# Check logs
tail -f logs/crawler.log

# Reduce concurrent requests
# Edit .env: CRAWLER_MAX_CONCURRENT_REQUESTS=5
```

**API 401 Unauthorized:**
```bash
# Verify API key in .env
cat .env | grep API_KEYS

# Use correct header name
# X-API-Key (not Authorization)
```

**Tests failing:**
```bash
# Install dev dependencies
pip install -r requirements.txt

# Check MongoDB is running
docker ps | grep mongodb

# Run specific test
pytest tests/unit/test_config.py -v
```

## Python API Usage

```python
import asyncio
from src.crawler import BooksCrawler
from src.database import db_client

async def main():
    # Connect to database
    await db_client.connect()

    # Run crawler
    async with BooksCrawler() as crawler:
        await crawler.crawl_all()

    # Get statistics
    stats = await db_client.get_stats()
    print(f"Total books: {stats.total_books}")

    # Disconnect
    await db_client.disconnect()

asyncio.run(main())
```

## File Locations

- **Logs**: `logs/crawler.log`
- **Checkpoints**: `data/checkpoints/crawler_state.json`
- **Sample data**: `data/sample/books.json`
- **Config**: `.env`
- **Tests**: `tests/`
- **Documentation**: `docs/`

## Performance Tuning

### For faster crawling:
```env
CRAWLER_MAX_CONCURRENT_REQUESTS=20
CRAWLER_REQUEST_DELAY=0.1
```

### For gentler crawling:
```env
CRAWLER_MAX_CONCURRENT_REQUESTS=5
CRAWLER_REQUEST_DELAY=1.0
```

### For production API:
```env
API_WORKERS=4
RATE_LIMIT_PER_MINUTE=120
```

## Monitoring

### Check application status:
```bash
# API health
curl http://localhost:8000/health

# View logs
tail -f logs/crawler.log

# Container stats
docker stats

# Database stats
python -m src stats
```

## Security Checklist

- [ ] Generate strong API keys (32+ characters)
- [ ] Enable MongoDB authentication
- [ ] Use HTTPS in production
- [ ] Configure firewall rules
- [ ] Enable rate limiting
- [ ] Regular security updates
- [ ] Rotate API keys monthly
- [ ] Monitor access logs
- [ ] Use environment variables for secrets
- [ ] Enable CORS restrictions

## Support

- **Documentation**: `/docs` folder
- **API Docs**: http://localhost:8000/docs
- **GitHub Issues**: https://github.com/yourusername/books-crawler/issues
