# Developer Playbook: Books-to-Scrape Web Crawler

## Overview

This playbook provides a complete step-by-step guide for developing, deploying, and maintaining a production-ready web crawler for the Books to Scrape website.

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────┐
│                    Client Applications                   │
│          (CLI, API Consumers, Monitoring Tools)          │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  FastAPI REST API                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Auth & Rate  │  │  Endpoints   │  │   Health     │  │
│  │   Limiting   │  │   Handler    │  │   Checks     │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│  Async   │  │ MongoDB  │  │Scheduler │
│ Crawler  │──│ Database │  │  (APSch) │
│          │  │          │  │          │
└──────────┘  └──────────┘  └──────────┘
     │
     ├── Parser (BeautifulSoup)
     ├── Checkpoint Manager
     └── HTTP Client (aiohttp)
```

### Data Flow

1. **Crawl Initiation**: User triggers crawl via CLI or API
2. **URL Queue**: Crawler builds queue of URLs to visit
3. **Concurrent Fetching**: Multiple async workers fetch pages
4. **Parsing**: BeautifulSoup extracts book data
5. **Storage**: MongoDB stores/updates book records
6. **Checkpoint**: Progress saved for resume capability
7. **API Access**: REST API provides access to stored data

## Development Stages

### Stage 1: Local Development Setup

**Goal**: Set up development environment

```bash
# 1. Clone and setup
git clone <repository>
cd books-crawler
python -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start MongoDB (Docker)
docker run -d -p 27017:27017 --name mongodb mongo:7.0

# 4. Configure environment
cp .env.example .env
# Edit .env with your settings

# 5. Run tests
pytest

# 6. Start development server
python -m src api
```

### Stage 2: Crawler Development

**Goal**: Build robust web crawler

**Key Files**:
- `src/crawler/__init__.py` - Main crawler logic
- `src/crawler/parser.py` - HTML parsing
- `src/crawler/checkpoint.py` - Resume capability

**Testing Strategy**:
```bash
# Unit tests for parser
pytest tests/unit/test_parser.py -v

# Integration tests with mock HTTP
pytest tests/integration/ -v

# Manual testing
python -m src crawl
```

**Performance Optimization**:
- Adjust `CRAWLER_MAX_CONCURRENT_REQUESTS` (default: 10)
- Tune `CRAWLER_REQUEST_DELAY` for rate limiting
- Monitor memory usage during large crawls

### Stage 3: Database Integration

**Goal**: Implement MongoDB storage with change tracking

**Schema Design**:
```javascript
// Books collection with indexes
db.books.createIndex({ "url": 1 }, { unique: true })
db.books.createIndex({ "category": 1 })
db.books.createIndex({ "price": 1 })
db.books.createIndex({ "last_scraped_at": -1 })
```

**Change Detection**:
- Price history tracking via `price_history` array
- `scrape_count` increments on each crawl
- `last_scraped_at` timestamp for freshness

### Stage 4: API Development

**Goal**: Build secure REST API

**Security Layers**:
1. API Key authentication (header-based)
2. Rate limiting (per IP/API key)
3. Input validation (Pydantic)
4. CORS configuration

**Endpoints to Test**:
```bash
# Health check
curl http://localhost:8000/health

# Get books (requires API key)
curl -H "X-API-Key: test-key" \
  http://localhost:8000/api/v1/books

# Start crawl
curl -X POST -H "X-API-Key: test-key" \
  http://localhost:8000/api/v1/crawl/start
```

### Stage 5: Scheduler Integration

**Goal**: Automated periodic crawling

**Configuration**:
```env
SCHEDULER_ENABLED=true
SCHEDULER_INTERVAL_HOURS=24
SCHEDULER_TIMEZONE=UTC
```

**Jobs**:
1. **Periodic Crawl**: Full site crawl (configurable interval)
2. **Change Detection**: Compare current vs. previous data (hourly)

### Stage 6: Docker Containerization

**Goal**: Package application for deployment

**Build & Test**:
```bash
# Build image
docker build -t books-crawler .

# Test container
docker run -p 8000:8000 \
  -e MONGODB_URL=mongodb://host.docker.internal:27017 \
  -e API_KEYS=test-key \
  books-crawler

# Use docker-compose
docker-compose up -d
```

**Production Considerations**:
- Multi-stage builds for smaller images
- Non-root user for security
- Health checks for orchestration
- Volume mounts for persistence

### Stage 7: Testing Strategy

**Test Pyramid**:

```
        ▲
       ╱ ╲
      ╱E2E╲         E2E: Full workflow tests
     ╱─────╲
    ╱  INT  ╲       Integration: API + DB
   ╱─────────╲
  ╱   UNIT    ╲     Unit: Parser, Models, etc.
 ╱─────────────╲
```

**Coverage Goals**:
- Unit tests: > 80%
- Integration tests: Critical paths
- E2E tests: Major workflows

**Running Tests**:
```bash
# All tests with coverage
pytest --cov=src --cov-report=html

# Specific suites
pytest tests/unit/ -v
pytest tests/integration/ -v

# Watch mode for development
pytest-watch
```

### Stage 8: CI/CD Pipeline

**Goal**: Automated testing and deployment

**Pipeline Stages** (GitHub Actions):

1. **Lint & Format**
   - Ruff for code quality
   - Black for formatting (optional)

2. **Type Check**
   - MyPy for type safety

3. **Test**
   - Unit tests
   - Integration tests
   - Coverage reporting

4. **Build**
   - Docker image build
   - Multi-platform support

5. **Security Scan**
   - Trivy for vulnerabilities
   - Dependency checking

**Deployment Strategy**:
```yaml
# On push to main
- Build production image
- Tag with version/commit
- Push to registry
- Deploy to staging
- Run smoke tests
- Deploy to production
```

## Production Deployment

### Pre-deployment Checklist

- [ ] Environment variables configured
- [ ] API keys generated and secured
- [ ] MongoDB backup strategy in place
- [ ] Monitoring and alerting configured
- [ ] Rate limits tuned for production
- [ ] SSL/TLS certificates installed
- [ ] DNS records configured
- [ ] Health checks working

### Deployment Options

#### Option 1: Docker Compose (Single Server)

```bash
# Production docker-compose
docker-compose -f docker-compose.prod.yml up -d
```

#### Option 2: Kubernetes

```bash
# Deploy to k8s cluster
kubectl apply -f k8s/deployment.yml
kubectl apply -f k8s/service.yml
kubectl apply -f k8s/ingress.yml
```

#### Option 3: Cloud Platform (AWS/GCP/Azure)

- Use managed MongoDB (Atlas, DocumentDB)
- Container service (ECS, Cloud Run, AKS)
- Load balancer for API
- Auto-scaling based on load

### Monitoring

**Key Metrics**:
- Crawl success/failure rate
- API response times
- Database query performance
- Memory and CPU usage
- Active connections

**Tools**:
- Prometheus + Grafana
- Application logs
- Database monitoring
- APM (e.g., New Relic, DataDog)

### Maintenance

**Regular Tasks**:
- Monitor crawl statistics
- Check for failed requests
- Review price changes
- Optimize database indexes
- Update dependencies
- Rotate API keys
- Backup database

**Troubleshooting**:

| Issue | Solution |
|-------|----------|
| Crawl too slow | Increase concurrent requests |
| Too many errors | Check website availability |
| Database slow | Add/optimize indexes |
| API timeouts | Increase timeout, scale workers |
| Memory issues | Reduce batch size, add limits |

## Best Practices

### Code Quality

- Use type hints throughout
- Write docstrings for all functions
- Follow PEP 8 style guide
- Keep functions small and focused
- Use async/await properly

### Error Handling

- Catch specific exceptions
- Log errors with context
- Implement retry logic
- Fail gracefully
- Provide meaningful error messages

### Performance

- Use connection pooling
- Implement caching where appropriate
- Batch database operations
- Monitor resource usage
- Profile slow operations

### Security

- Validate all inputs
- Sanitize data before storage
- Use parameterized queries
- Keep dependencies updated
- Follow OWASP guidelines
- Implement rate limiting
- Use HTTPS in production

## Advanced Topics

### Distributed Crawling

For large-scale crawling:
- Message queue (RabbitMQ, Redis)
- Multiple worker instances
- Centralized checkpoint storage
- Load balancing

### Machine Learning Integration

Potential enhancements:
- Price prediction models
- Book recommendation engine
- Category classification
- Sentiment analysis of reviews

### API Extensions

Additional features:
- GraphQL endpoint
- WebSocket for real-time updates
- Webhook notifications
- Export to CSV/JSON
- Search with Elasticsearch

## Conclusion

This playbook provides a comprehensive guide for building a production-ready web crawler. By following these steps and best practices, you'll have a robust, scalable, and maintainable system.

For questions or contributions, please open an issue or pull request.
