# Architecture Overview

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            CLIENT LAYER                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐          │
│  │   CLI    │    │  cURL/   │    │  Python  │    │  Web     │          │
│  │  Client  │    │  Postman │    │  Client  │    │  Browser │          │
│  └────┬─────┘    └────┬─────┘    └────┬─────┘    └────┬─────┘          │
│       │               │               │               │                 │
└───────┼───────────────┼───────────────┼───────────────┼─────────────────┘
        │               │               │               │
        └───────────────┴───────────────┴───────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         API GATEWAY LAYER                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                         NGINX/Reverse Proxy                      │    │
│  │                      (SSL/TLS, Load Balancing)                   │    │
│  └──────────────────────────────┬───────────────────────────────────┘    │
│                                 │                                        │
└─────────────────────────────────┼────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       APPLICATION LAYER                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                        FastAPI Application                         │  │
│  ├───────────────────────────────────────────────────────────────────┤  │
│  │                                                                     │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐│  │
│  │  │ Auth & Rate  │  │   Routers    │  │  Health & Monitoring     ││  │
│  │  │   Limiting   │  │  (Endpoints) │  │     (Metrics)            ││  │
│  │  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────────┘│  │
│  │         │                 │                       │                │  │
│  │         └─────────────────┴───────────────────────┘                │  │
│  │                           │                                         │  │
│  └───────────────────────────┼─────────────────────────────────────────┘  │
│                              │                                           │
│              ┌───────────────┼────────────────┐                          │
│              │               │                │                          │
│              ▼               ▼                ▼                          │
│  ┌──────────────────┐ ┌─────────────┐ ┌───────────────┐                │
│  │  Crawler Engine  │ │  Scheduler  │ │  DB Manager   │                │
│  └──────────────────┘ └─────────────┘ └───────────────┘                │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
                │                 │                 │
                ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       BUSINESS LOGIC LAYER                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                      Crawler Components                          │    │
│  ├─────────────────────────────────────────────────────────────────┤    │
│  │                                                                   │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │    │
│  │  │   Parser     │  │  Checkpoint  │  │   Retry Manager      │  │    │
│  │  │ (BS4/HTML)   │  │   Manager    │  │  (Exponential Back)  │  │    │
│  │  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │    │
│  │         │                 │                       │              │    │
│  │         └─────────────────┴───────────────────────┘              │    │
│  │                           │                                       │    │
│  │  ┌────────────────────────▼──────────────────────────────────┐  │    │
│  │  │              HTTP Client (aiohttp)                        │  │    │
│  │  │         Async Request Pool + Semaphore Control           │  │    │
│  │  └───────────────────────┬───────────────────────────────────┘  │    │
│  └──────────────────────────┼──────────────────────────────────────┘    │
│                             │                                            │
│  ┌──────────────────────────┼──────────────────────────────────────┐    │
│  │                Scheduler (APScheduler)                           │    │
│  ├──────────────────────────┼──────────────────────────────────────┤    │
│  │  ┌──────────────────┐    │    ┌──────────────────────────┐     │    │
│  │  │ Periodic Crawl   │    │    │  Change Detection Job    │     │    │
│  │  │   (24h default)  │    │    │     (Hourly default)     │     │    │
│  │  └──────────────────┘    │    └──────────────────────────┘     │    │
│  └──────────────────────────┼──────────────────────────────────────┘    │
│                             │                                            │
└─────────────────────────────┼────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        DATA LAYER                                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                        MongoDB Database                            │  │
│  ├───────────────────────────────────────────────────────────────────┤  │
│  │                                                                     │  │
│  │  ┌──────────────────────────────────────────────────────────────┐ │  │
│  │  │  books Collection                                             │ │  │
│  │  ├──────────────────────────────────────────────────────────────┤ │  │
│  │  │  Indexes:                                                     │ │  │
│  │  │  - url (unique)                                               │ │  │
│  │  │  - category                                                   │ │  │
│  │  │  - price                                                      │ │  │
│  │  │  - last_scraped_at                                            │ │  │
│  │  ├──────────────────────────────────────────────────────────────┤ │  │
│  │  │  Documents:                                                   │ │  │
│  │  │  {                                                            │ │  │
│  │  │    _id, url, title, price, rating, category,                 │ │  │
│  │  │    availability, description, image_url,                      │ │  │
│  │  │    first_scraped_at, last_scraped_at, scrape_count,          │ │  │
│  │  │    price_history: [{price, changed_at}, ...]                 │ │  │
│  │  │  }                                                            │ │  │
│  │  └──────────────────────────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                           │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                  Checkpoint Storage (JSON)                         │  │
│  │    - visited_urls, pending_urls, completed_categories             │  │
│  │    - crawler state for resume capability                          │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       EXTERNAL LAYER                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                    books.toscrape.com                              │  │
│  │                  (Target Website)                                  │  │
│  │                                                                     │  │
│  │  - Homepage (Category Links)                                       │  │
│  │  - Category Pages (Book Listings)                                  │  │
│  │  - Book Detail Pages (Full Information)                            │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Crawling Flow

```
1. Start Crawl Request
   │
   ├─→ Load Checkpoint (if resume)
   │
   ├─→ Fetch Homepage
   │   └─→ Extract Category URLs
   │
   ├─→ For Each Category:
   │   │
   │   ├─→ Fetch Category Page
   │   │   └─→ Extract Book URLs
   │   │
   │   ├─→ For Each Book URL:
   │   │   │
   │   │   ├─→ Check if Visited (Checkpoint)
   │   │   │
   │   │   ├─→ Fetch Book Detail Page
   │   │   │   └─→ Parse Book Data
   │   │   │
   │   │   ├─→ Store in MongoDB
   │   │   │   ├─→ New Book: Insert
   │   │   │   └─→ Existing: Update + Track Changes
   │   │   │
   │   │   └─→ Mark as Visited (Checkpoint)
   │   │
   │   └─→ Pagination: Fetch Next Page
   │
   └─→ Save Final Checkpoint
```

### API Request Flow

```
1. Client Request
   │
   ├─→ NGINX/Reverse Proxy
   │   └─→ SSL Termination
   │
   ├─→ FastAPI App
   │   │
   │   ├─→ API Key Validation
   │   │   └─→ (401 if invalid)
   │   │
   │   ├─→ Rate Limit Check
   │   │   └─→ (429 if exceeded)
   │   │
   │   ├─→ Request Validation (Pydantic)
   │   │   └─→ (422 if invalid)
   │   │
   │   ├─→ Business Logic
   │   │   └─→ Database Query/Operation
   │   │
   │   ├─→ Response Formation
   │   │
   │   └─→ Return Response
   │
   └─→ Client Receives Response
```

## Component Interactions

### Crawler ↔ Database
- Crawler fetches and parses data
- Database stores/updates books
- Change detection on price updates
- Timestamp tracking for freshness

### API ↔ Database
- API queries database for book data
- Filtering and pagination support
- Statistics aggregation
- Read-only access (safe for concurrent use)

### Scheduler ↔ Crawler
- Scheduler triggers periodic crawls
- Asynchronous execution
- Independent of API requests
- Configurable intervals

### Checkpoint ↔ Crawler
- Checkpoint saves progress periodically
- Resume capability on failure
- Atomic file operations
- JSON-based storage

## Scalability Considerations

### Horizontal Scaling
- Multiple API instances (load balanced)
- Distributed crawling (message queue)
- Database replica sets
- Containerized deployment

### Vertical Scaling
- Adjust concurrent requests
- Increase worker threads
- Database connection pooling
- Memory optimization

## Security Layers

1. **Network**: Firewall, SSL/TLS
2. **API**: Key authentication, rate limiting
3. **Application**: Input validation, error handling
4. **Data**: MongoDB auth, encrypted connections
5. **Container**: Non-root user, minimal image
