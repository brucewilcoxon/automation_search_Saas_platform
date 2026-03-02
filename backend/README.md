# Auction Navigator Backend

Production-ready backend scaffold for the Auction Navigator Suite.

> **📖 New to the project?** See [SETUP_GUIDE.md](../SETUP_GUIDE.md) for a complete step-by-step setup guide.

## Tech Stack

- **Python 3.11**
- **FastAPI** - Modern, fast web framework
- **MySQL** - Relational database
- **Redis** - Caching and Celery broker
- **SQLAlchemy** - ORM
- **Alembic** - Database migrations
- **Celery** - Async task processing

## Project Structure

```
backend/
├── app/                    # FastAPI application
│   ├── api/               # API route handlers
│   ├── core/              # Core configuration and database
│   └── schemas/           # Pydantic schemas
├── db/                    # Database models and migrations
│   ├── models/            # SQLAlchemy models
│   └── migrations/        # Alembic migration files
workers/                   # Celery workers
├── tasks/                 # Celery task definitions
scrapers/                  # Scraping adapters
└── adapters/              # County-specific adapters
```

## Database Models

- **counties** - County information
- **auction_sources** - Auction data sources
- **auction_events** - Auction events
- **auction_items** - Individual auction items
- **parcels** - Property parcels
- **ingest_runs** - Scraper run tracking

## API Endpoints

### Health Check
- `GET /health` - Health check endpoint

### Auctions
- `GET /api/auctions?state=&county=` - Get auction events with optional filters

### Auction Items
- `GET /api/auction-items?event_id=` - Get items for a specific auction event

### Parcels
- `GET /api/parcels?parcel_id=` - Get parcels with optional filter
- `GET /api/parcels/{parcel_id}/comps?window=6m` - Get comparable sales for a parcel (6 months)
- `GET /api/parcels/{parcel_id}/comps?window=12m` - Get comparable sales for a parcel (12 months)

### Ingestion
- `POST /api/ingest/run` - Start an ingestion run for a state and county
  - Request body: `{ "state": "FL", "county": "Miami-Dade" }`
  - Returns: Job ID and run ID
- `GET /api/ingest/status/{job_id}` - Get status of an ingestion job
- `GET /api/ingest/runs` - List all ingestion runs with pagination
  - Query params: `limit` (default 50), `offset` (default 0)

### Cash Buyers
- `GET /api/cash-buyers` - Get cash buyers with optional filters
  - Query params: `state`, `county`, `date_from`, `date_to`, `min_volume`, `q` (search)

### Letters
- `POST /api/letters/templates` - Create a new letter template
- `GET /api/letters/templates` - Get all letter templates
- `POST /api/letters/campaigns` - Create a new letter campaign
  - Request body: `{ "parcel_ids": [...], "template_id": "...", "merge_fields": {...} }`
- `GET /api/letters/campaigns/{campaign_id}` - Get a letter campaign by ID
- `POST /api/letters/{letter_id}/send` - Send a letter (stub with logging)

### Reports
- `POST /api/reports/auction-pdf` - Generate PDF report for auction parcel/event
  - Request body: `{ "parcel_id": "...", "event_id": "..." }`
  - Returns: PDF file download

## Running Locally

### Prerequisites

- **Python 3.11** installed
- **MySQL 8.0+** installed and running (default port 3306)
- **Redis 7** installed and running (default port 6379)
- Ports 3306 (MySQL), 6379 (Redis), and 8000 (API) available

### Setup Steps

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up MySQL database:**
   ```bash
   # Create database (if not exists)
   mysql -u root -p -e "CREATE DATABASE auction_navigator CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
   
   # Or using MySQL client:
   mysql -u root -p
   CREATE DATABASE auction_navigator CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

3. **Set environment variables:**
   
   Create a `.env` file in the project root:
   ```env
   DATABASE_URL=mysql+pymysql://root:password@localhost:3306/auction_navigator?charset=utf8mb4
   REDIS_URL=redis://localhost:6379/0
   ENVIRONMENT=development
   DEBUG=true
   LOG_LEVEL=INFO
   CORS_ORIGINS=http://localhost:5173,http://localhost:3000
   ```
   
   Or export them in your shell:
   ```bash
   export DATABASE_URL=mysql+pymysql://root:password@localhost:3306/auction_navigator?charset=utf8mb4
   export REDIS_URL=redis://localhost:6379/0
   ```
   
   **Note**: Replace `root` and `password` with your MySQL username and password.

4. **Run database migrations:**
   ```bash
   alembic -c backend/db/alembic.ini upgrade head
   ```

5. **Start the API server:**
   ```bash
   uvicorn backend.app.main:app --reload
   ```
   
   The API will be available at http://localhost:8000
   API documentation at http://localhost:8000/docs

6. **Start Celery worker (in separate terminal):**
   ```bash
   celery -A workers.celery_app worker --loglevel=info
   ```

7. **Start Celery beat (optional, for scheduled tasks):**
   ```bash
   celery -A workers.celery_app beat --loglevel=info
   ```

### Accessing Services

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **MySQL**: localhost:3306
- **Redis**: localhost:6379

## Database Migrations

### Create a new migration:
```bash
alembic -c backend/db/alembic.ini revision --autogenerate -m "description"
```

### Apply migrations:
```bash
alembic -c backend/db/alembic.ini upgrade head
```

### Rollback migration:
```bash
alembic -c backend/db/alembic.ini downgrade -1
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov=scrapers --cov=workers

# Run specific test file
pytest tests/test_parcel_normalization.py

# Run with verbose output
pytest -v
```

### Test Coverage

- **Parcel normalization**: Tests for parcel ID normalization logic
- **Adapter parsing**: Tests for HTML parsing using saved fixtures

### Code Formatting

```bash
# TODO: Add formatting tools (black, ruff)
black backend/
ruff check backend/
```

## Production Deployment

For production deployment:

1. Set `ENVIRONMENT=production` and `DEBUG=false`
2. Use proper database credentials
3. Configure CORS origins appropriately
4. Use a production WSGI server (gunicorn with uvicorn workers)
5. Set up proper logging and monitoring
6. Use environment-specific configuration files

## Troubleshooting

### Migration Errors

**Problem**: `alembic.util.exc.CommandError: Target database is not up to date`

**Solution**:
```bash
# Check current migration status
alembic -c backend/db/alembic.ini current

# Upgrade to head
alembic -c backend/db/alembic.ini upgrade head

# If that fails, check for conflicts
alembic -c backend/db/alembic.ini heads
```

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'backend'`

**Solution**:
- Ensure you're running from the project root
- Ensure `PYTHONPATH` includes the project root:
  ```bash
  export PYTHONPATH="${PYTHONPATH}:$(pwd)"
  ```
- Or install the package in development mode:
  ```bash
  pip install -e .
  ```

### Database Connection Errors

**Problem**: `pymysql.err.OperationalError: could not connect to server`

**Solution**:
- Check MySQL is running: `systemctl status mysql` or `brew services list` (macOS)
- Verify DATABASE_URL in environment variables matches your MySQL setup
- Test connection: `mysql -u root -p -e "USE auction_navigator; SELECT 1;"`
- Check MySQL is listening on port 3306: `netstat -tulpn | grep 3306` or `lsof -i :3306`
- Verify MySQL user has proper permissions: `GRANT ALL PRIVILEGES ON auction_navigator.* TO 'root'@'localhost';`

### Redis Connection Errors

**Problem**: `redis.exceptions.ConnectionError: Error connecting to Redis`

**Solution**:
- Check Redis is running: `redis-cli ping` (should return PONG)
- Verify REDIS_URL in environment variables (default: `redis://localhost:6379/0`)
- Test connection: `python -c "import redis; r=redis.from_url('redis://localhost:6379/0'); r.ping()"`
- Check Redis is listening on port 6379: `netstat -tulpn | grep 6379`

### Celery Task Not Running

**Problem**: Tasks are queued but not executing

**Solution**:
- Verify worker is running: Check the terminal where you started `celery -A workers.celery_app worker`
- Check Redis connection: Ensure Redis is running and REDIS_URL is correct
- Check worker logs for errors
- Restart worker: Stop and restart the Celery worker process
- Verify Celery can connect to Redis: `celery -A workers.celery_app inspect ping`

### PDF Generation Errors

**Problem**: `weasyprint` fails to generate PDF

**Solution**:
- Ensure system dependencies are installed (cairo, pango, etc.)
- Install system packages:
  ```bash
  # Ubuntu/Debian
  sudo apt-get install libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
  
  # macOS (using Homebrew)
  brew install cairo pango gdk-pixbuf libffi
  
  # Fedora/RHEL
  sudo dnf install cairo pango pangocairo gdk-pixbuf2 libffi-devel
  ```

### Port Already in Use

**Problem**: `Address already in use` when starting services

**Solution**:
- Check what's using the port: `lsof -i :8000` (or `netstat -tulpn | grep 8000` on Linux)
- Stop conflicting services
- For MySQL/Redis, ensure no other instances are running on the same ports
- Change the port in your uvicorn command: `uvicorn backend.app.main:app --port 8001`

### CORS Errors in Frontend

**Problem**: `CORS policy: No 'Access-Control-Allow-Origin' header`

**Solution**:
- Verify CORS_ORIGINS includes your frontend URL in `.env` file
- Check frontend is using correct API base URL
- Restart API server: Stop and restart `uvicorn backend.app.main:app --reload`
- Verify CORS_ORIGINS is set correctly: Check your `.env` file or environment variables

## Environment Variables

All configuration is done via environment variables. Key variables:

```env
# Database
DATABASE_URL=mysql+pymysql://user:pass@host:port/dbname?charset=utf8mb4

# Redis
REDIS_URL=redis://host:port/db

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
FRONTEND_DOMAIN=https://yourdomain.com  # Production

# Environment
ENVIRONMENT=development|production
DEBUG=true|false
LOG_LEVEL=DEBUG|INFO|WARNING|ERROR

# Scraping
SCRAPER_RATE_LIMIT_REQUESTS=10
SCRAPER_RATE_LIMIT_WINDOW=60
SCRAPER_RETRY_MAX_ATTEMPTS=3
SCRAPER_TIMEOUT=30

# Email
EMAIL_PROVIDER=stub|sendgrid|mailgun
EMAIL_FROM_ADDRESS=noreply@example.com
```

## Next Steps

- [x] Implement actual scraping logic in adapters
- [x] Add comprehensive error handling
- [x] Add logging and monitoring
- [x] Add unit and integration tests
- [ ] Add authentication and authorization
- [ ] Add request validation and rate limiting (API level)
- [ ] Add API documentation enhancements
- [ ] Set up CI/CD pipeline
