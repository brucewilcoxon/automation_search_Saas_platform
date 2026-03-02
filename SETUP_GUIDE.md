# Auction Navigator Suite - Setup Guide

Complete step-by-step guide to get the project running locally.

> **👋 New to programming/development?** See [BEGINNER_GUIDE.md](BEGINNER_GUIDE.md) for a more detailed guide with explanations of everything.

## Prerequisites

Before starting, ensure you have the following installed:

- **Python 3.11** or higher
- **MySQL 8.0+** installed and running
- **Redis** installed and running
- **Git** (to clone the repository if needed)

### Verify Prerequisites

```bash
# Check Python version
python --version
# Should show Python 3.11.x or higher

# Check MySQL
mysql --version
# Should show MySQL 8.0.x or higher

# Check Redis
redis-cli --version
# Should show redis-cli version

# Check if MySQL is running
# On Linux:
sudo systemctl status mysql
# On macOS:
brew services list | grep mysql
# On Windows:
# Check Services app for MySQL service
```

## Step-by-Step Setup

### Step 1: Clone/Navigate to Project

If you haven't already, navigate to the project directory:

```bash
cd auction-navigator-suite-main
```

### Step 2: Create Python Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# You should see (venv) in your terminal prompt
```

### Step 3: Install Python Dependencies

```bash
# Make sure you're in the project root directory
pip install --upgrade pip
pip install -r requirements.txt
```

This will install all required packages including:
- FastAPI and Uvicorn
- SQLAlchemy and Alembic
- PyMySQL (MySQL driver)
- Celery and Redis
- WeasyPrint (PDF generation)
- And all other dependencies

### Step 4: Set Up MySQL Database

#### 4.1 Start MySQL Service

```bash
# On Linux:
sudo systemctl start mysql
# On macOS:
brew services start mysql
# On Windows:
# MySQL should start automatically, or start it from Services
```

#### 4.2 Create Database

```bash
# Connect to MySQL (you'll be prompted for root password)
mysql -u root -p

# Once connected, run:
CREATE DATABASE auction_navigator CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# Verify database was created
SHOW DATABASES;

# Exit MySQL
EXIT;
```

#### 4.3 (Optional) Create Dedicated MySQL User

For better security, create a dedicated user:

```bash
mysql -u root -p

# Create user
CREATE USER 'auction_user'@'localhost' IDENTIFIED BY 'your_secure_password';

# Grant privileges
GRANT ALL PRIVILEGES ON auction_navigator.* TO 'auction_user'@'localhost';

# Apply changes
FLUSH PRIVILEGES;

EXIT;
```

### Step 5: Set Up Redis

#### 5.1 Start Redis Service

```bash
# On Linux:
sudo systemctl start redis
# On macOS:
brew services start redis
# On Windows:
# Start Redis from Services or run redis-server
```

#### 5.2 Verify Redis is Running

```bash
redis-cli ping
# Should return: PONG
```

### Step 6: Configure Environment Variables

Create a `.env` file in the project root directory:

```bash
# In the project root, create .env file
touch .env  # On macOS/Linux
# Or create it manually on Windows
```

Add the following content to `.env`:

```env
# Database Configuration
DATABASE_URL=mysql+pymysql://root:your_mysql_password@localhost:3306/auction_navigator?charset=utf8mb4
# If you created a dedicated user, use:
# DATABASE_URL=mysql+pymysql://auction_user:your_secure_password@localhost:3306/auction_navigator?charset=utf8mb4

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Application Settings
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# CORS Configuration (for frontend)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Optional: Frontend Domain (for production)
# FRONTEND_DOMAIN=https://yourdomain.com
```

**Important**: Replace `your_mysql_password` with your actual MySQL root password (or the dedicated user's password).

### Step 7: Run Database Migrations

```bash
# Make sure you're in the project root directory
# And your virtual environment is activated

# Run all migrations
alembic -c backend/db/alembic.ini upgrade head
```

You should see output like:
```
INFO  [alembic.runtime.migration] Context impl MySQLImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 001_initial, Initial schema
INFO  [alembic.runtime.migration] Running upgrade 001_initial -> 002_add_raw_json, Add raw_json columns
...
```

### Step 8: Verify Database Tables

```bash
# Connect to MySQL
mysql -u root -p

# Use the database
USE auction_navigator;

# List all tables
SHOW TABLES;

# You should see tables like:
# - counties
# - auction_sources
# - auction_events
# - auction_items
# - parcels
# - comparable_sales
# - ingest_runs
# - cash_buyers
# - letter_templates
# - letter_campaigns
# - letters
# - reports

EXIT;
```

### Step 9: Start the API Server

Open a new terminal window/tab and:

```bash
# Navigate to project directory
cd auction-navigator-suite-main

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Start the API server
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see output like:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Step 10: Start Celery Worker (Optional but Recommended)

Open another terminal window/tab:

```bash
# Navigate to project directory
cd auction-navigator-suite-main

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Start Celery worker
celery -A workers.celery_app worker --loglevel=info
```

You should see output like:
```
[tasks]
  . workers.tasks.scraper_tasks.run_ingestion_task

[2024-01-XX XX:XX:XX,XXX: INFO/MainProcess] Connected to redis://localhost:6379/0
[2024-01-XX XX:XX:XX,XXX: INFO/MainProcess] celery@hostname ready.
```

### Step 11: (Optional) Start Celery Beat Scheduler

If you need scheduled tasks, open another terminal:

```bash
# Navigate to project directory
cd auction-navigator-suite-main

# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Start Celery beat
celery -A workers.celery_app beat --loglevel=info
```

## Verification

### Test the API

1. **Health Check**:
   ```bash
   curl http://localhost:8000/health
   # Or open in browser: http://localhost:8000/health
   ```
   Should return: `{"status":"healthy","timestamp":"...","service":"auction-navigator-api"}`

2. **API Documentation**:
   Open in browser: http://localhost:8000/docs
   
   You should see the interactive Swagger UI with all available endpoints.

3. **Test an Endpoint**:
   ```bash
   # Get auctions (will be empty initially)
   curl http://localhost:8000/api/auctions
   
   # Get ingestion runs (will be empty initially)
   curl http://localhost:8000/api/ingest/runs
   ```

### Verify Services are Running

```bash
# Check MySQL
mysql -u root -p -e "SELECT 1;"

# Check Redis
redis-cli ping

# Check API (should return JSON)
curl http://localhost:8000/health
```

## Running the Full Stack

You'll need **3 terminal windows** running simultaneously:

### Terminal 1: API Server
```bash
cd auction-navigator-suite-main
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 2: Celery Worker
```bash
cd auction-navigator-suite-main
source venv/bin/activate  # or venv\Scripts\activate on Windows
celery -A workers.celery_app worker --loglevel=info
```

### Terminal 3: (Optional) Celery Beat
```bash
cd auction-navigator-suite-main
source venv/bin/activate  # or venv\Scripts\activate on Windows
celery -A workers.celery_app beat --loglevel=info
```

## Common Issues and Solutions

### Issue: "ModuleNotFoundError: No module named 'backend'"

**Solution**:
```bash
# Make sure you're in the project root directory
pwd  # Should show the auction-navigator-suite-main directory

# Set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
# On Windows PowerShell:
$env:PYTHONPATH = "$(Get-Location);$env:PYTHONPATH"
```

### Issue: "pymysql.err.OperationalError: (2003, 'Can\'t connect to MySQL server')"

**Solution**:
1. Check MySQL is running:
   ```bash
   # Linux
   sudo systemctl status mysql
   # macOS
   brew services list | grep mysql
   ```
2. Verify connection string in `.env` file
3. Test connection manually:
   ```bash
   mysql -u root -p -e "SELECT 1;"
   ```

### Issue: "redis.exceptions.ConnectionError: Error connecting to Redis"

**Solution**:
1. Check Redis is running:
   ```bash
   redis-cli ping  # Should return PONG
   ```
2. Start Redis if not running:
   ```bash
   # Linux
   sudo systemctl start redis
   # macOS
   brew services start redis
   ```

### Issue: "alembic.util.exc.CommandError: Target database is not up to date"

**Solution**:
```bash
# Check current migration status
alembic -c backend/db/alembic.ini current

# Upgrade to latest
alembic -c backend/db/alembic.ini upgrade head

# If issues persist, check for conflicts
alembic -c backend/db/alembic.ini heads
```

### Issue: "Port 8000 already in use"

**Solution**:
```bash
# Find what's using the port
# On Linux/macOS:
lsof -i :8000
# On Windows:
netstat -ano | findstr :8000

# Kill the process or use a different port:
uvicorn backend.app.main:app --reload --port 8001
```

### Issue: "ImportError: cannot import name 'X' from 'Y'"

**Solution**:
1. Make sure all dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```
2. Verify virtual environment is activated
3. Check you're in the project root directory

## Next Steps

Once everything is running:

1. **Explore the API**: Visit http://localhost:8000/docs
2. **Test Endpoints**: Try the health check and other endpoints
3. **Run Tests**: `pytest` (from project root)
4. **Start Ingesting Data**: Use `POST /api/ingest/run` to start data collection
5. **Connect Frontend**: Point your frontend to `http://localhost:8000`

## Quick Reference

### Start Everything (3 terminals)

**Terminal 1 - API**:
```bash
source venv/bin/activate && uvicorn backend.app.main:app --reload
```

**Terminal 2 - Worker**:
```bash
source venv/bin/activate && celery -A workers.celery_app worker --loglevel=info
```

**Terminal 3 - Beat** (optional):
```bash
source venv/bin/activate && celery -A workers.celery_app beat --loglevel=info
```

### Useful Commands

```bash
# Check migration status
alembic -c backend/db/alembic.ini current

# Create new migration
alembic -c backend/db/alembic.ini revision --autogenerate -m "description"

# Run tests
pytest

# Check MySQL connection
mysql -u root -p -e "USE auction_navigator; SHOW TABLES;"

# Check Redis connection
redis-cli ping
```

## Support

If you encounter issues not covered here:
1. Check the logs in your terminal windows
2. Verify all services (MySQL, Redis) are running
3. Check your `.env` file configuration
4. Review the troubleshooting section in `backend/README.md`
