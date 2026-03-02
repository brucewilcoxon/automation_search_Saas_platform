# Quick Start Guide - Windows

**Simplest way to get the project running on Windows**

## Step 1: Install Required Programs

### 1. Python
- Download from: https://www.python.org/downloads/
- **Important**: Check "Add Python to PATH" during installation
- Verify: Open Command Prompt, type `python --version`

### 2. MySQL
- Download from: https://dev.mysql.com/downloads/installer/
- Choose "MySQL Installer for Windows"
- During installation, create a password and **write it down!**
- Verify: Search for "MySQL Command Line Client" and log in

### 3. Redis (Easiest Option)
- Download Memurai: https://www.memurai.com/get-memurai
- Install it (it's free)
- It starts automatically
- Verify: Open Command Prompt, type `memurai-cli ping` (should see PONG)

## Step 2: Set Up Project

### Open PowerShell or Command Prompt

1. **Navigate to your project folder:**
   ```powershell
   cd "F:\Workana, Oursourcing task\3. Automated search website - 700\auction-navigator-suite-main"
   ```

2. **Create virtual environment:**
   ```powershell
   python -m venv venv
   ```

3. **Activate virtual environment:**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
   If you get an error about execution policy, run this first:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```
   Then try activating again.

4. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```
   (This takes 5-15 minutes)

## Step 3: Set Up Database

1. **Create database in MySQL:**
   - Open "MySQL Command Line Client"
   - Enter your password
   - Type: `CREATE DATABASE auction_navigator CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;`
   - Type: `exit`

2. **Create .env file:**
   - In your project folder, create a file named `.env`
   - Put this content in it (replace YOUR_PASSWORD with your MySQL password):
   ```
   DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/auction_navigator?charset=utf8mb4
   REDIS_URL=redis://localhost:6379/0
   ENVIRONMENT=development
   DEBUG=true
   LOG_LEVEL=INFO
   CORS_ORIGINS=http://localhost:5173,http://localhost:3000
   ```

3. **Run migrations:**
   ```powershell
   alembic -c backend/db/alembic.ini upgrade head
   ```

## Step 4: Start the Application

### Open TWO PowerShell/Command Prompt windows

**Window 1 - API Server:**
```powershell
cd "F:\Workana, Oursourcing task\3. Automated search website - 700\auction-navigator-suite-main"
.\venv\Scripts\Activate.ps1
uvicorn backend.app.main:app --reload
```

**Window 2 - Worker:**
```powershell
cd "F:\Workana, Oursourcing task\3. Automated search website - 700\auction-navigator-suite-main"
.\venv\Scripts\Activate.ps1
celery -A workers.celery_app worker --loglevel=info
```

## Step 5: Test It

Open your browser and go to:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

If you see the API documentation page, **you're done!** ✅

## Troubleshooting

**"python is not recognized"**
- Reinstall Python and check "Add Python to PATH"
- Restart your computer

**"Execution Policy" error in PowerShell**
- Run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- Then try activating venv again

**"Can't connect to MySQL"**
- Make sure MySQL service is running (check Services)
- Verify password in .env file is correct

**"redis-cli not found"**
- If using Memurai, use `memurai-cli ping` instead
- Or make sure Redis service is running

**Need more help?**
- See [BEGINNER_GUIDE.md](BEGINNER_GUIDE.md) for detailed explanations
- See [SETUP_GUIDE.md](SETUP_GUIDE.md) for more advanced setup
