# Getting Started Guide

## Quick Start (5 Minutes)

### Option 1: Docker (Recommended)

```bash
# 1. Clone repository
git clone https://github.com/Shaon2221/web-crawling-playbook.git
cd web-crawling-playbook

# 2. Configure environment
cp .env.example .env
# Edit .env and set API_KEYS=your-secret-key

# 3. Start services
docker-compose up -d

# 4. Check status
docker-compose ps
docker-compose logs -f crawler-api

# 5. Access API
curl http://localhost:8000/health

# 6. View documentation
# Open http://localhost:8000/docs in browser
```

### Option 2: Local Development

```bash
# 1. Prerequisites
# - Python 3.11+
# - MongoDB 7.0+

# 2. Setup
git clone https://github.com/Shaon2221/web-crawling-playbook.git
cd web-crawling-playbook

# 3. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Configure environment
cp .env.example .env
nano .env  # Edit configuration

# 6. Start MongoDB
docker run -d -p 27017:27017 --name mongodb mongo:7.0

# 7. Run crawler
python -m src crawl

# 8. Start API
python -m src api
```

### Option 3: Automated Setup Script

```bash
# Run the setup script
chmod +x scripts/setup.sh
./scripts/setup.sh

# Follow on-screen instructions
```

## First Steps

### 1. Run Your First Crawl

```bash
# Using CLI
python -m src crawl

# Using Docker
docker-compose run --rm crawler-worker

# Expected output:
# INFO - Crawler started
# INFO - Starting full crawl
# INFO - Found 50 categories
# INFO - Crawling category: Fiction
# INFO - Scraped book: Book Title
# ...
```

### 2. Check the Results

```bash
# View statistics
python -m src stats

# Or via API
curl -H "X-API-Key: your-key" \
  http://localhost:8000/api/v1/books/stats
```

### 3. Query Books via API

```bash
# Get all books
curl -H "X-API-Key: your-key" \
  "http://localhost:8000/api/v1/books?limit=10" | jq

# Filter by category
curl -H "X-API-Key: your-key" \
  "http://localhost:8000/api/v1/books?category=Fiction" | jq

# Filter by price range
curl -H "X-API-Key: your-key" \
  "http://localhost:8000/api/v1/books?min_price=10&max_price=30" | jq
```

### 4. Explore Interactive Documentation

Open in your browser:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Common Tasks

### Start API Server

```bash
# Development mode (with reload)
uvicorn src.api:app --reload

# Production mode
python -m src api

# With custom port
python -m src api --port 8080
```

### Run Crawler

```bash
# Full crawl
python -m src crawl

# Resume from checkpoint
python -m src crawl --resume

# Background crawl
nohup python -m src crawl > crawler.log 2>&1 &
```

### View Logs

```bash
# Real-time logs
tail -f logs/crawler.log

# Search logs
grep ERROR logs/crawler.log

# Docker logs
docker-compose logs -f
```

### Database Operations

```bash
# Connect to MongoDB
docker exec -it mongodb mongosh

# In mongosh:
use books_crawler
db.books.countDocuments()
db.books.find().limit(5)

# Backup database
docker exec mongodb mongodump --out=/backup
```

## Configuration Examples

### Low-Impact Crawling (Gentle)

```env
CRAWLER_MAX_CONCURRENT_REQUESTS=3
CRAWLER_REQUEST_DELAY=2.0
CRAWLER_TIMEOUT=60
```

### High-Speed Crawling (Aggressive)

```env
CRAWLER_MAX_CONCURRENT_REQUESTS=20
CRAWLER_REQUEST_DELAY=0.1
CRAWLER_TIMEOUT=15
```

### Production API

```env
API_WORKERS=4
RATE_LIMIT_PER_MINUTE=120
LOG_LEVEL=WARNING
```

### Development API

```env
API_RELOAD=true
API_WORKERS=1
RATE_LIMIT_PER_MINUTE=300
LOG_LEVEL=DEBUG
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific tests
pytest tests/unit/test_parser.py -v

# Run integration tests only
pytest tests/integration/ -v

# Watch mode (continuous testing)
ptw  # requires pytest-watch
```

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/my-feature
```

### 2. Make Changes

```bash
# Edit code
nano src/crawler/parser.py

# Run tests
pytest

# Format code
black src/
ruff check --fix src/
```

### 3. Commit Changes

```bash
git add .
git commit -m "feat: add new feature"
```

### 4. Push and Create PR

```bash
git push origin feature/my-feature
# Create pull request on GitHub
```

## Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError`
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

**Issue**: `Connection refused` (MongoDB)
```bash
# Solution: Start MongoDB
docker start mongodb
# or
docker run -d -p 27017:27017 --name mongodb mongo:7.0
```

**Issue**: `Port 8000 already in use`
```bash
# Solution: Find and kill process
lsof -ti:8000 | xargs kill -9
# or use different port
python -m src api --port 8080
```

**Issue**: API returns 401 Unauthorized
```bash
# Solution: Check API key
cat .env | grep API_KEYS
# Use correct header
curl -H "X-API-Key: your-actual-key" ...
```

## Next Steps

1. **Read the Documentation**
   - [README.md](README.md) - Full documentation
   - [docs/API.md](docs/API.md) - API reference
   - [docs/PLAYBOOK.md](docs/PLAYBOOK.md) - Developer guide

2. **Explore the Code**
   - Review `src/crawler/__init__.py` for crawler logic
   - Check `src/api/__init__.py` for API endpoints
   - Examine `src/database/__init__.py` for DB operations

3. **Customize**
   - Modify `.env` for your needs
   - Extend API endpoints
   - Add custom parsers
   - Implement new features

4. **Deploy**
   - Follow [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)
   - Set up production environment
   - Configure monitoring
   - Enable backups

## Getting Help

- **Documentation**: Check `/docs` directory
- **Issues**: GitHub Issues
- **API Docs**: http://localhost:8000/docs
- **Quick Reference**: [docs/QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md)

## Tips for Success

1. **Start Small**: Run a test crawl with low concurrency
2. **Monitor Logs**: Watch logs to understand behavior
3. **Use Checkpoints**: Enable resume for reliability
4. **Test Locally**: Validate changes before deploying
5. **Read Docs**: Comprehensive documentation available
6. **Ask Questions**: Open issues for help

---

Happy Crawling! 🚀
