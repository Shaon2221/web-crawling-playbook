# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-01

### Added
- Initial release of Books-to-Scrape web crawler
- Async web crawler with configurable concurrency
- Retry mechanism with exponential backoff
- Resume capability with checkpoint system
- MongoDB integration for data storage
- Price history tracking and change detection
- FastAPI REST API with Swagger documentation
- API key authentication
- Rate limiting (per minute)
- APScheduler for periodic crawling
- Comprehensive logging with rotation
- Docker and docker-compose support
- Unit and integration tests
- GitHub Actions CI/CD pipeline
- Complete documentation (README, API docs, Playbook)
- Sample data and examples
- CLI for crawler operations
- Health check endpoints
- Error handling and monitoring

### Features
- **Crawler**
  - Async HTTP requests with aiohttp
  - BeautifulSoup4 for HTML parsing
  - Configurable concurrent requests (default: 10)
  - Request delay and timeout settings
  - Automatic retry with backoff
  - Checkpoint-based resume
  - Category-based crawling

- **Database**
  - MongoDB storage
  - Unique URL indexing
  - Price history tracking
  - Change detection
  - Scrape count and timestamps
  - Optimized indexes for queries

- **API**
  - RESTful endpoints
  - API key authentication
  - Rate limiting (60 req/min default)
  - Pagination support
  - Filtering by category and price
  - Statistics endpoint
  - Crawl control endpoints
  - Health checks

- **Scheduler**
  - Periodic crawling (24h default)
  - Change detection (hourly)
  - Configurable timezone
  - Job management

- **DevOps**
  - Multi-stage Docker build
  - Docker Compose setup
  - CI/CD with GitHub Actions
  - Automated testing
  - Security scanning
  - Pre-commit hooks
  - Makefile for common tasks

### Documentation
- Comprehensive README
- API documentation
- Developer playbook
- Deployment guide
- Contributing guidelines
- Sample data and examples

### Testing
- Unit tests for core components
- Integration tests for API
- Test coverage reporting
- Pytest configuration
- Mock fixtures for testing

### Security
- API key authentication
- Rate limiting
- Input validation
- Non-root Docker user
- Environment variable management
- Secrets handling

[1.0.0]: https://github.com/yourusername/books-crawler/releases/tag/v1.0.0
