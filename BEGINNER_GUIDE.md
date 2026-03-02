# Complete Beginner's Guide - Auction Navigator Suite

This guide is written for people who have **never done programming or development before**. We'll explain everything step by step.

## What You Need to Know First

**What is this project?**
- It's a web application (like a website) that helps people find and analyze property auctions
- It has a **backend** (the server that does the work) and a **frontend** (what users see in their browser)
- This guide will help you run the **backend** part

**What you'll be doing:**
- Installing some programs on your computer
- Running some commands (typing text into a terminal/command prompt)
- Starting a server that makes the application work

**Don't worry if you don't understand everything!** Just follow the steps one by one.

---

## Part 1: Installing Required Programs

You need to install 4 programs on your computer. We'll do this one at a time.

### Step 1.1: Install Python

**What is Python?** It's a programming language. Our project needs it to run.

**How to install:**

1. **Go to**: https://www.python.org/downloads/
2. **Click** the big yellow button that says "Download Python 3.11.x" (or latest version)
3. **Run the downloaded file** (it will be something like `python-3.11.x.exe`)
4. **Important**: When the installer opens, check the box that says **"Add Python to PATH"** at the bottom
5. **Click** "Install Now"
6. **Wait** for it to finish
7. **Click** "Close"

**How to verify it worked:**
- Press `Windows Key + R` (or search for "Run")
- Type `cmd` and press Enter
- In the black window that opens, type: `python --version`
- Press Enter
- You should see something like: `Python 3.11.x`

✅ **If you see a version number, Python is installed!**

❌ **If you see "python is not recognized":**
- Python might not be in your PATH
- Try reinstalling Python and make sure to check "Add Python to PATH"
- Or restart your computer after installation

---

### Step 1.2: Install MySQL

**What is MySQL?** It's a database program that stores all the data (like auction information).

**How to install:**

1. **Go to**: https://dev.mysql.com/downloads/installer/
2. **Choose**: "MySQL Installer for Windows" (the first option)
3. **Download** the file (it's large, about 400MB, so it may take a while)
4. **Run the downloaded file**
5. **Choose**: "Developer Default" (this installs everything you need)
6. **Click** "Next" through the screens
7. **When asked for a password**: Create a password and **write it down!** You'll need it later.
   - Example: `MyPassword123!`
   - **Save this password somewhere safe**
8. **Click** "Next" and "Execute" to install
9. **Wait** for installation to complete (this takes 10-20 minutes)
10. **Click** "Finish"

**How to verify it worked:**
- Press `Windows Key` and search for "MySQL Command Line Client"
- Click on it
- Enter the password you created
- You should see: `mysql>`
- Type: `exit` and press Enter to close

✅ **If you can log in, MySQL is installed!**

---

### Step 1.3: Install Redis

**What is Redis?** It's a program that helps the application work faster by storing temporary data.

**For Windows - Easiest Method:**

**Option 1: Using Memurai (Recommended - Windows Native, Easiest)**

1. **Go to**: https://www.memurai.com/get-memurai
2. **Click** "Download Memurai Developer Edition" (it's free)
3. **Download** the installer file
4. **Run the installer** and click "Next" through the installation
5. **It will start automatically** after installation

**How to verify it worked:**
- Open Command Prompt (cmd)
- Type: `memurai-cli ping`
- You should see: `PONG`

✅ **If you see PONG, Redis is working!**

**Option 2: Using WSL (If you already have WSL installed)**

If WSL is already on your computer:

1. **Open Ubuntu** (search for "Ubuntu" in Start menu)
   - If you don't have Ubuntu, you can install it from Microsoft Store

2. **In Ubuntu, type these commands one by one:**
   ```bash
   sudo apt update
   sudo apt install redis-server -y
   sudo service redis-server start
   ```

3. **To verify**, in Ubuntu type:
   ```bash
   redis-cli ping
   ```
   Should return: `PONG`

**Option 3: Skip Redis for Now (Not Recommended)**

If Redis is too difficult to install, you can skip it for now, but some features (like background tasks) won't work. The API server will still run.

**Important**: If you use Memurai, update your `.env` file later - it should still work with `REDIS_URL=redis://localhost:6379/0`

---

### Step 1.4: Install Git (Optional but Helpful)

**What is Git?** It's a tool for managing code. You might already have it.

1. **Go to**: https://git-scm.com/download/win
2. **Download** and install (just click Next through everything)
3. **Verify**: Open Command Prompt and type: `git --version`
   - You should see a version number

---

## Part 2: Setting Up the Project

### Step 2.1: Open Command Prompt

**On Windows:**
- Press `Windows Key + R`
- Type: `cmd`
- Press Enter
- A black window will open - this is where you'll type commands

**Or:**
- Press `Windows Key`
- Type: `cmd`
- Click on "Command Prompt"

### Step 2.2: Navigate to Your Project Folder

**What does "navigate" mean?** It means going to the folder where your project files are.

1. **Find your project folder:**
   - It's probably in: `F:\Workana, Oursourcing task\3. Automated search website - 700\auction-navigator-suite-main`
   - Or wherever you saved/extracted the project

2. **In Command Prompt, type:**
   ```cmd
   cd "F:\Workana, Oursourcing task\3. Automated search website - 700\auction-navigator-suite-main"
   ```
   **Important**: Replace the path with YOUR actual project folder path!

   **Tip**: You can also:
   - Open the project folder in Windows Explorer
   - Click in the address bar (where it shows the folder path)
   - Copy the path
   - In Command Prompt, type: `cd ` (with a space after cd)
   - Right-click in the Command Prompt window and select "Paste"
   - Press Enter

3. **Verify you're in the right place:**
   ```cmd
   dir
   ```
   You should see files like: `requirements.txt`, `README.md`, and folders like `backend`, `frontend`

✅ **If you see these files, you're in the right place!**

---

### Step 2.3: Create a Virtual Environment

**What is a virtual environment?** It's like a separate box for Python packages so they don't mix with other projects.

**In Command Prompt, type:**
```cmd
python -m venv venv
```

**Wait** for it to finish (it takes 30 seconds to 2 minutes).

**You should see the prompt come back** (no errors).

---

### Step 2.4: Activate the Virtual Environment

**Type this command:**
```cmd
venv\Scripts\activate
```

**You should see** `(venv)` appear at the beginning of your command prompt line, like this:
```
(venv) F:\Workana, Oursourcing task\3. Automated search website - 700\auction-navigator-suite-main>
```

✅ **If you see (venv), it's activated!**

**Important**: Every time you open a NEW Command Prompt window to work on this project, you need to:
1. Navigate to the project folder (`cd "your path"`)
2. Activate the virtual environment (`venv\Scripts\activate`)

---

### Step 2.5: Install Project Dependencies

**What are dependencies?** They're the extra programs (called "packages") that this project needs to work.

**Type these commands one by one:**
```cmd
python -m pip install --upgrade pip
```

Wait for it to finish, then:
```cmd
pip install -r requirements.txt
```

**This will take 5-15 minutes** depending on your internet speed. You'll see lots of text scrolling by - that's normal!

**Wait until you see** the command prompt again (the `(venv)` line).

✅ **If the command finished without errors, dependencies are installed!**

---

## Part 3: Setting Up the Database

### Step 3.1: Start MySQL

**Make sure MySQL is running:**

1. Press `Windows Key` and search for "Services"
2. Open "Services"
3. Look for "MySQL80" or "MySQL" in the list
4. If it says "Running" - you're good! ✅
5. If it says "Stopped":
   - Right-click on it
   - Click "Start"
   - Wait until it says "Running"

---

### Step 3.2: Create the Database

1. **Open MySQL Command Line Client:**
   - Press `Windows Key`
   - Search for "MySQL Command Line Client"
   - Click on it

2. **Enter your password** (the one you created when installing MySQL)
   - Press Enter

3. **You should see**: `mysql>`

4. **Type this command** (copy and paste it):
   ```sql
   CREATE DATABASE auction_navigator CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
   Press Enter

5. **You should see**: `Query OK, 1 row affected`

6. **Type**: `exit` and press Enter to close MySQL

✅ **Database is created!**

---

## Part 4: Configure the Project

### Step 4.1: Create the .env File

**What is a .env file?** It's a configuration file that tells the project how to connect to your database.

1. **Open Notepad** (or any text editor)

2. **Copy and paste this text:**
   ```
   DATABASE_URL=mysql+pymysql://root:YOUR_MYSQL_PASSWORD@localhost:3306/auction_navigator?charset=utf8mb4
   REDIS_URL=redis://localhost:6379/0
   ENVIRONMENT=development
   DEBUG=true
   LOG_LEVEL=INFO
   CORS_ORIGINS=http://localhost:5173,http://localhost:3000
   ```

3. **Replace `YOUR_MYSQL_PASSWORD`** with the actual password you created for MySQL
   - For example, if your password is `MyPassword123!`, it should look like:
   ```
   DATABASE_URL=mysql+pymysql://root:MyPassword123!@localhost:3306/auction_navigator?charset=utf8mb4
   ```

4. **Save the file:**
   - Click "File" → "Save As"
   - **Important**: Navigate to your project folder
   - In "File name", type: `.env` (with the dot at the beginning!)
   - In "Save as type", choose "All Files" (not Text Document)
   - Click "Save"

✅ **The .env file is created!**

**Note**: If you can't see the file after saving, that's normal - files starting with a dot are sometimes hidden. It's there!

---

### Step 4.2: Run Database Migrations

**What are migrations?** They create all the tables (like spreadsheets) in your database.

**In Command Prompt** (make sure you're in the project folder and venv is activated):

```cmd
alembic -c backend/db/alembic.ini upgrade head
```

**Wait** for it to finish. You should see messages like:
```
INFO  [alembic.runtime.migration] Running upgrade  -> 001_initial, Initial schema
INFO  [alembic.runtime.migration] Running upgrade 001_initial -> 002_add_raw_json, Add raw_json columns
...
```

✅ **If you see "Running upgrade" messages, migrations worked!**

---

## Part 5: Starting the Application

You need to open **TWO Command Prompt windows** and run different things in each.

### Step 5.1: Start the API Server (First Window)

1. **Open a NEW Command Prompt window**
   - Press `Windows Key + R`
   - Type: `cmd`
   - Press Enter

2. **Navigate to your project folder:**
   ```cmd
   cd "F:\Workana, Oursourcing task\3. Automated search website - 700\auction-navigator-suite-main"
   ```
   (Use YOUR actual path)

3. **Activate virtual environment:**
   ```cmd
   venv\Scripts\activate
   ```

4. **Start the server:**
   ```cmd
   uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **You should see:**
   ```
   INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
   INFO:     Started reloader process
   INFO:     Started server process
   INFO:     Waiting for application startup.
   INFO:     Application startup complete.
   ```

✅ **The server is running!**

**Keep this window open!** Don't close it. The server needs to keep running.

---

### Step 5.2: Start the Worker (Second Window)

1. **Open ANOTHER Command Prompt window**
   - Press `Windows Key + R`
   - Type: `cmd`
   - Press Enter

2. **Navigate to your project folder:**
   ```cmd
   cd "F:\Workana, Oursourcing task\3. Automated search website - 700\auction-navigator-suite-main"
   ```

3. **Activate virtual environment:**
   ```cmd
   venv\Scripts\activate
   ```

4. **Start the worker:**
   ```cmd
   celery -A workers.celery_app worker --loglevel=info
   ```

5. **You should see:**
   ```
   [tasks]
     . workers.tasks.scraper_tasks.run_ingestion_task
   
   [INFO/MainProcess] Connected to redis://localhost:6379/0
   [INFO/MainProcess] celery@hostname ready.
   ```

✅ **The worker is running!**

**Keep this window open too!**

---

## Part 6: Testing That Everything Works

### Step 6.1: Open Your Web Browser

1. **Open any web browser** (Chrome, Firefox, Edge, etc.)

2. **Go to this address:**
   ```
   http://localhost:8000/health
   ```

3. **You should see** something like:
   ```json
   {
     "status": "healthy",
     "timestamp": "2024-01-XX...",
     "service": "auction-navigator-api"
   }
   ```

✅ **If you see this, the API is working!**

---

### Step 6.2: Check the API Documentation

1. **In your browser, go to:**
   ```
   http://localhost:8000/docs
   ```

2. **You should see** a page with "Swagger UI" and a list of API endpoints

✅ **If you see this page, everything is set up correctly!**

---

## Part 7: What to Do Next

### Your Application is Now Running!

You have:
- ✅ API Server running (Terminal 1)
- ✅ Worker running (Terminal 2)
- ✅ Database set up
- ✅ Everything connected

### To Use the Application:

1. **API Documentation**: http://localhost:8000/docs
   - This shows all available endpoints
   - You can test them directly from this page

2. **Health Check**: http://localhost:8000/health
   - This tells you if the server is running

3. **Connect the Frontend**: 
   - If you have the frontend part, point it to `http://localhost:8000`

---

## Common Problems and Solutions

### Problem: "python is not recognized"

**Solution:**
- Python might not be installed correctly
- Try reinstalling Python and make sure to check "Add Python to PATH"
- Restart your computer after installing

---

### Problem: "mysql is not recognized"

**Solution:**
- MySQL might not be in your PATH
- Try using the full path: `"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p`
- Or use MySQL Workbench (a graphical tool) instead

---

### Problem: "redis-cli is not recognized"

**Solution:**
- If you're using WSL, make sure you're running the command inside Ubuntu
- If you're using Memurai, the command might be different
- Try: `memurai-cli ping` instead

---

### Problem: "ModuleNotFoundError: No module named 'backend'"

**Solution:**
1. Make sure you're in the project root folder
2. Make sure the virtual environment is activated (you see `(venv)` in your prompt)
3. Try this command:
   ```cmd
   set PYTHONPATH=%CD%
   ```
   Then try running your command again

---

### Problem: "Can't connect to MySQL server"

**Solution:**
1. Make sure MySQL is running (check Services)
2. Check your password in the `.env` file is correct
3. Try connecting manually:
   ```cmd
   mysql -u root -p
   ```
   Enter your password. If this works, MySQL is fine - the problem is in the connection string.

---

### Problem: "Error connecting to Redis"

**Solution:**
1. Make sure Redis is running
2. If using WSL, make sure Redis is started:
   ```bash
   sudo service redis-server start
   ```
3. Test connection: `redis-cli ping` (should return PONG)

---

### Problem: "Port 8000 already in use"

**Solution:**
- Something else is using port 8000
- You can use a different port:
  ```cmd
  uvicorn backend.app.main:app --reload --port 8001
  ```
- Then access it at: http://localhost:8001

---

### Problem: Command Prompt closes immediately

**Solution:**
- This usually means there's an error
- Open Command Prompt manually first
- Then navigate to your folder
- Then run the command
- This way you can see the error message

---

## Quick Reference: Starting the Project

**Every time you want to work on this project:**

### Terminal 1 (API Server):
```cmd
cd "F:\Workana, Oursourcing task\3. Automated search website - 700\auction-navigator-suite-main"
venv\Scripts\activate
uvicorn backend.app.main:app --reload
```

### Terminal 2 (Worker):
```cmd
cd "F:\Workana, Oursourcing task\3. Automated search website - 700\auction-navigator-suite-main"
venv\Scripts\activate
celery -A workers.celery_app worker --loglevel=info
```

**Then open**: http://localhost:8000/docs in your browser

---

## Getting Help

If you get stuck:

1. **Read the error message carefully** - it often tells you what's wrong
2. **Check the Common Problems section** above
3. **Make sure all services are running**:
   - MySQL (check Services)
   - Redis (test with `redis-cli ping`)
4. **Check your .env file** has the correct password
5. **Make sure you're in the right folder** and virtual environment is activated

---

## What Each Part Does (Simple Explanation)

- **Python**: The programming language the project uses
- **MySQL**: Stores all the data (like a filing cabinet)
- **Redis**: Makes things faster (like a quick-access drawer)
- **Virtual Environment**: Keeps this project's packages separate from other projects
- **API Server**: The main program that handles requests
- **Worker**: Does background tasks (like downloading data)
- **.env file**: Contains your passwords and settings (like a key)

---

## You're Done! 🎉

If you followed all these steps and can see http://localhost:8000/docs in your browser, **congratulations!** The project is running.

**Remember:**
- Keep both Command Prompt windows open while you're using the project
- Close them when you're done (press CTRL+C in each window first, then close)
- Next time you want to use it, just follow the "Quick Reference" section above

Good luck! 🚀
