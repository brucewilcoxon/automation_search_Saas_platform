# Deploy Auction Navigator Suite to a VPS via GitHub

Step-by-step guide: push the project to GitHub, then clone and run it on a Linux VPS.

---

## Part 1: Push Your Project to GitHub (from your PC)

### Step 1.1: Install Git (if needed)

- Download: https://git-scm.com/download/win  
- Install with default options.  
- Verify in PowerShell: `git --version`

### Step 1.2: Create a GitHub repository

1. Log in to https://github.com  
2. Click **“+”** → **“New repository”**  
3. Set **Repository name** (e.g. `auction-navigator-suite`)  
4. Choose **Private** or **Public**  
5. **Do not** add README, .gitignore, or license (project already has them)  
6. Click **“Create repository”**

### Step 1.3: Push your local project to GitHub

Open **PowerShell** in your project folder:

```powershell
cd "F:\Workana, Oursourcing task\3. Automated search website - 700\auction-navigator-suite-main"
```

**If this folder is not yet a Git repo:**

```powershell
git init
git add .
git commit -m "Initial commit - Auction Navigator Suite"
```

**If it is already a Git repo**, just ensure everything is committed:

```powershell
git status
git add .
git commit -m "Prepare for VPS deployment"   # only if there are changes
```

**Add GitHub as remote and push** (replace `YOUR_USERNAME` and `YOUR_REPO` with your GitHub username and repo name):

```powershell
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

If GitHub asks for login, use a **Personal Access Token** as password (Settings → Developer settings → Personal access tokens).

**Important:** The `.env` file is in `.gitignore` and will **not** be pushed. You will create `.env` on the VPS with production values.

---

## Part 2: Set Up Your VPS

Use any Linux VPS (Ubuntu 22.04 recommended): DigitalOcean, Linode, Vultr, AWS EC2, etc.

### Step 2.1: Connect to the VPS

From your PC (PowerShell or any terminal):

```bash
ssh root@YOUR_VPS_IP
```

Or with a user: `ssh youruser@YOUR_VPS_IP`

### Step 2.2: Install system dependencies (Ubuntu/Debian)

Run on the VPS:

```bash
sudo apt update && sudo apt upgrade -y

# Python 3.11, pip, venv
sudo apt install -y python3.11 python3.11-venv python3-pip git

# MySQL
sudo apt install -y mysql-server
sudo systemctl start mysql
sudo systemctl enable mysql
sudo mysql_secure_installation   # set root password, answer prompts

# Redis
sudo apt install -y redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Node.js (for building frontend)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Optional: Nginx (reverse proxy)
sudo apt install -y nginx
```

### Step 2.3: Create MySQL database and user

```bash
sudo mysql -u root -p
```

In MySQL:

```sql
CREATE DATABASE auction_navigator CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'auction_user'@'localhost' IDENTIFIED BY 'CHOOSE_A_STRONG_PASSWORD';
GRANT ALL PRIVILEGES ON auction_navigator.* TO 'auction_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

Replace `CHOOSE_A_STRONG_PASSWORD` with a real password and save it for the `.env` file.

### Step 2.4: Clone the project from GitHub

```bash
cd /opt   # or any directory you prefer, e.g. /home/youruser
sudo git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git auction-navigator
sudo chown -R $USER:$USER auction-navigator
cd auction-navigator
```

Replace `YOUR_USERNAME/YOUR_REPO` with your actual GitHub repo URL. If the repo is private, use:

```bash
git clone https://YOUR_GITHUB_TOKEN@github.com/YOUR_USERNAME/YOUR_REPO.git auction-navigator
```

(Or set up SSH keys on the VPS and use the `git@github.com:...` URL.)

### Step 2.5: Python virtual environment and dependencies

```bash
cd /opt/auction-navigator   # or your path
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 2.6: Create `.env` on the VPS

```bash
nano .env
```

Paste (adjust passwords and URLs):

```env
DATABASE_URL=mysql+pymysql://auction_user:CHOOSE_A_STRONG_PASSWORD@localhost:3306/auction_navigator?charset=utf8mb4
REDIS_URL=redis://localhost:6379/0
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com,http://YOUR_VPS_IP
```

Save (Ctrl+O, Enter, Ctrl+X). **Do not** commit this file; it should stay only on the server.

### Step 2.7: Run database migrations

```bash
source venv/bin/activate
alembic -c backend/db/alembic.ini upgrade head
```

### Step 2.8: Build and serve the frontend (optional)

If you want the React UI on the VPS:

```bash
cd frontend
npm ci
npm run build
cd ..
```

The built files will be in `frontend/dist`. You can serve them with Nginx (see Step 2.10).

### Step 2.9: Run the API and Celery with systemd (recommended)

So the API and worker restart on reboot and crashes:

**1) API service**

```bash
sudo nano /etc/systemd/system/auction-api.service
```

Paste (fix paths and user if needed):

```ini
[Unit]
Description=Auction Navigator API
After=network.target mysql.service redis-server.service

[Service]
User=root
Group=root
WorkingDirectory=/opt/auction-navigator
Environment="PATH=/opt/auction-navigator/venv/bin"
ExecStart=/opt/auction-navigator/venv/bin/uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

**2) Celery worker service**

```bash
sudo nano /etc/systemd/system/auction-celery.service
```

```ini
[Unit]
Description=Auction Navigator Celery Worker
After=network.target redis-server.service

[Service]
User=root
Group=root
WorkingDirectory=/opt/auction-navigator
Environment="PATH=/opt/auction-navigator/venv/bin"
ExecStart=/opt/auction-navigator/venv/bin/celery -A workers.celery_app worker --loglevel=info
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

**3) Enable and start**

```bash
sudo systemctl daemon-reload
sudo systemctl enable auction-api auction-celery
sudo systemctl start auction-api auction-celery
sudo systemctl status auction-api auction-celery
```

API will be available at `http://YOUR_VPS_IP:8000`. Test: `curl http://localhost:8000/health`

### Step 2.10: (Optional) Nginx reverse proxy and frontend

To use a domain, HTTPS, and serve the frontend:

```bash
sudo nano /etc/nginx/sites-available/auction-navigator
```

Example (replace `yourdomain.com` and paths):

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Frontend (if you built it)
    root /opt/auction-navigator/frontend/dist;
    index index.html;
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    location /health { proxy_pass http://127.0.0.1:8000; }
    location /docs { proxy_pass http://127.0.0.1:8000; }
    location /openapi.json { proxy_pass http://127.0.0.1:8000; }
}
```

Enable and reload:

```bash
sudo ln -s /etc/nginx/sites-available/auction-navigator /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

For HTTPS, use Certbot: `sudo apt install certbot python3-certbot-nginx && sudo certbot --nginx -d yourdomain.com`

---

## Part 3: Updating the App After Changes (from GitHub)

On your PC: commit and push to GitHub as usual.

On the VPS:

```bash
cd /opt/auction-navigator
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
alembic -c backend/db/alembic.ini upgrade head
cd frontend && npm ci && npm run build && cd ..
sudo systemctl restart auction-api auction-celery
```

---

## Quick reference

| Step | Where | Action |
|------|--------|--------|
| 1 | PC | Create repo on GitHub, then `git init` / `git add` / `git commit` / `git remote add origin` / `git push` |
| 2 | VPS | Install Python 3.11, MySQL, Redis, Node; create DB and user |
| 3 | VPS | `git clone` repo, `python3.11 -m venv venv`, `pip install -r requirements.txt` |
| 4 | VPS | Create `.env` with `DATABASE_URL`, `REDIS_URL`, `CORS_ORIGINS`, etc. |
| 5 | VPS | `alembic -c backend/db/alembic.ini upgrade head` |
| 6 | VPS | Install systemd units for API and Celery, `systemctl enable --now auction-api auction-celery` |
| 7 | VPS | Optional: build frontend, configure Nginx and SSL |

---

## Security checklist

- Use a strong MySQL password and a dedicated DB user (not root).
- Never commit `.env` or tokens to GitHub.
- Prefer SSH keys for GitHub and VPS login.
- Keep the OS and packages updated: `sudo apt update && sudo apt upgrade -y`.
- Restrict firewall: e.g. allow only 22 (SSH), 80 (HTTP), 443 (HTTPS); keep 8000 only for localhost via Nginx.

If you tell me your VPS OS and whether you use a domain or only IP, I can adapt the Nginx and systemd steps exactly to your case.
