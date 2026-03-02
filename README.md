# Auction Navigator Suite

Full-stack application for navigating and analyzing property auctions.

## Quick Start

**Never done development before?** Start here: **[BEGINNER_GUIDE.md](BEGINNER_GUIDE.md)** - Complete beginner-friendly guide with explanations.

**Windows user?** Try **[QUICK_START_WINDOWS.md](QUICK_START_WINDOWS.md)** - Simplified Windows-specific guide.

**Have some experience?** See **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Step-by-step setup instructions.

For API documentation and details, see [backend/README.md](backend/README.md).

## Architecture

- **Frontend**: React + TypeScript (Vite)
- **Backend**: FastAPI (Python 3.11)
- **Database**: MySQL 8.0+
- **Cache/Queue**: Redis 7
- **Workers**: Celery
- **PDF Generation**: WeasyPrint + Jinja2

## Development

See [backend/README.md](backend/README.md) for detailed setup instructions, API documentation, and troubleshooting.

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov=scrapers --cov=workers
```

## License

Proprietary
