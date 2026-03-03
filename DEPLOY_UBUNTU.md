# Deploy to Ubuntu 20.04 (Property Radar USA)

Step-by-step guide to deploy **Property Radar USA** (Auction Navigator Suite) on Ubuntu 20.04.

- **GitHub**: https://github.com/brucewilcoxon/automation_search_Saas_platform  
- **Domain**: propertyradarusa.com  
- **VPS IP**: 138.117.216.204  

---

## Prerequisites

1. **VPS**: Ubuntu 20.04 server at `138.117.216.204` with root or sudo access.
2. **DNS**: Point your domain to the VPS:
   - Create an **A** record: `propertyradarusa.com` → `138.117.216.204`
   - (Optional) `www.propertyradarusa.com` → `138.117.216.204`
3. **SSH**: You can log in with `ssh root@138.117.216.204` (or your sudo user).

---

## Overview

| Component    | Role |
|-------------|------|
| **Nginx**  | Reverse proxy, SSL, serve frontend static files, proxy `/api` to backend |
| **Gunicorn** | Run FastAPI app (uvicorn workers) |
| **Celery** | Background tasks (scraping, etc.) |
| **MySQL**  | Database |
| **Redis**  | Cache + Celery broker |

---

## Step 1: Initial server setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Optional: create a dedicated app user (recommended)
sudo adduser --disabled-password --gecos "" appuser
sudo usermod -aG sudo appuser  # if this user should have sudo
```

---

## Step 2: Run the setup script (recommended)

From the project root on your **local machine**, copy the setup script to the server and run it:

```bash
# From your local project directory
scp scripts/setup_server.sh root@138.117.216.204:/tmp/
ssh root@138.117.216.204 "chmod +x /tmp/setup_server.sh"
```

**If the script was edited or copied from Windows**, fix line endings on the server before running:

```bash
ssh root@138.117.216.204 "sed -i 's/\r$//' /tmp/setup_server.sh"
```

Then on the **server**:

```bash
# Optional: override defaults (defaults: APP_DIR=/var/www/propertyradarusa, DOMAIN=propertyradarusa.com)
export APP_DIR=/var/www/propertyradarusa
export DOMAIN=propertyradarusa.com
export GITHUB_URL=https://github.com/brucewilcoxon/automation_search_Saas_platform.git
# Optional: enable SSL during setup (DNS must already point to this server)
# export RUN_CERTBOT=yes

sudo -E /tmp/setup_server.sh
```

The script will:

- Install Python 3.11, Node.js 18, MySQL 8, Redis, Nginx, and build dependencies for WeasyPrint
- Create the database and a dedicated DB user (random password saved to `.env`)
- Clone the repo and set up a Python venv, install dependencies, create `.env`
- Run database migrations and build the frontend
- Configure Nginx and systemd for the API and Celery worker
- Optionally run Certbot for SSL (`RUN_CERTBOT=yes`)

---

## Step 3: Manual setup (if not using the script)

### 3.1 Install system packages

```bash
sudo apt update
sudo apt install -y software-properties-common curl build-essential
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev

# Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# MySQL 8
sudo apt install -y mysql-server
sudo systemctl start mysql
sudo systemctl enable mysql
sudo mysql_secure_installation

# Redis
sudo apt install -y redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Nginx
sudo apt install -y nginx

# WeasyPrint / PDF dependencies
sudo apt install -y libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
```

### 3.2 Create MySQL database and user

```bash
sudo mysql -e "CREATE DATABASE auction_navigator CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
sudo mysql -e "CREATE USER 'pradar'@'localhost' IDENTIFIED BY 'YourSecurePassword';"
sudo mysql -e "GRANT ALL PRIVILEGES ON auction_navigator.* TO 'pradar'@'localhost';"
sudo mysql -e "FLUSH PRIVILEGES;"
```

Use the same credentials in `.env` as `DATABASE_URL`.

### 3.3 Clone repository and set up app

```bash
export APP_DIR=/var/www/propertyradarusa
sudo mkdir -p "$(dirname "$APP_DIR")"
sudo git clone https://github.com/brucewilcoxon/automation_search_Saas_platform.git "$APP_DIR"
cd "$APP_DIR"
```

### 3.4 Python environment and backend

```bash
sudo python3.11 -m venv venv
sudo venv/bin/pip install --upgrade pip
sudo venv/bin/pip install -r requirements.txt
```

Create `.env` in the project root (`$APP_DIR`):

```env
DATABASE_URL=mysql+pymysql://pradar:YourSecurePassword@127.0.0.1:3306/auction_navigator?charset=utf8mb4
REDIS_URL=redis://127.0.0.1:6379/0
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
FRONTEND_DOMAIN=https://propertyradarusa.com
CORS_ORIGINS=https://propertyradarusa.com,https://www.propertyradarusa.com
```

Run migrations (from `$APP_DIR`):

```bash
cd "$APP_DIR"
sudo venv/bin/alembic -c backend/db/alembic.ini upgrade head
```

### 3.5 Build frontend

```bash
cd "$APP_DIR/frontend"
sudo npm ci
sudo npm run build
```

The frontend uses `/api` as the API base URL; Nginx will proxy `/api` to the backend, so no frontend env change is required.

### 3.6 Nginx configuration

Create `/etc/nginx/sites-available/propertyradarusa`:

```nginx
server {
    listen 80;
    server_name propertyradarusa.com www.propertyradarusa.com;
    root /var/www/propertyradarusa/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /health {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }
}
```

Enable and test:

```bash
sudo ln -sf /etc/nginx/sites-available/propertyradarusa /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

### 3.7 SSL with Certbot (Let's Encrypt)

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d propertyradarusa.com -d www.propertyradarusa.com
```

Follow prompts. Certbot will adjust Nginx for HTTPS.

### 3.8 Systemd services

**API (Gunicorn)** — `/etc/systemd/system/propertyradarusa-api.service`:

```ini
[Unit]
Description=Property Radar USA API (Gunicorn)
After=network.target mysql.service redis-server.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/propertyradarusa
Environment="PATH=/var/www/propertyradarusa/venv/bin"
EnvironmentFile=/var/www/propertyradarusa/.env
ExecStart=/var/www/propertyradarusa/venv/bin/gunicorn backend.app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 127.0.0.1:8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

**Celery worker** — `/etc/systemd/system/propertyradarusa-celery.service`:

```ini
[Unit]
Description=Property Radar USA Celery Worker
After=network.target mysql.service redis-server.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/propertyradarusa
Environment="PATH=/var/www/propertyradarusa/venv/bin"
EnvironmentFile=/var/www/propertyradarusa/.env
ExecStart=/var/www/propertyradarusa/venv/bin/celery -A workers.celery_app worker --loglevel=info
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Then:

```bash
# Ensure .env and app files are readable by www-data
sudo chown -R www-data:www-data /var/www/propertyradarusa

sudo systemctl daemon-reload
sudo systemctl enable propertyradarusa-api propertyradarusa-celery
sudo systemctl start propertyradarusa-api propertyradarusa-celery
sudo systemctl status propertyradarusa-api propertyradarusa-celery
```

---

## Step 4: Verify deployment

1. **HTTPS**: Open `https://propertyradarusa.com` — you should see the app.
2. **API**: Open `https://propertyradarusa.com/api/health` or `https://propertyradarusa.com/docs` (if you expose it) and confirm the API responds.
3. **Logs**:
   - API: `sudo journalctl -u propertyradarusa-api -f`
   - Celery: `sudo journalctl -u propertyradarusa-celery -f`
   - Nginx: `sudo tail -f /var/log/nginx/error.log`

---

## Step 5: Updating the app

```bash
cd /var/www/propertyradarusa
sudo git pull
sudo venv/bin/pip install -r requirements.txt
sudo venv/bin/alembic -c backend/db/alembic.ini upgrade head
cd frontend && sudo npm ci && sudo npm run build
sudo systemctl restart propertyradarusa-api propertyradarusa-celery
```

---

## Firewall (optional)

If you use UFW:

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

---

## Troubleshooting

| Issue | Check |
|-------|------|
| 502 Bad Gateway | API not running: `sudo systemctl status propertyradarusa-api`; check `journalctl -u propertyradarusa-api` |
| Database connection error | Verify `DATABASE_URL` in `.env`, MySQL is running, and user has access to `auction_navigator` |
| CORS errors | Set `FRONTEND_DOMAIN` and/or `CORS_ORIGINS` in `.env` to `https://propertyradarusa.com` and reload API |
| Celery tasks not running | Ensure Redis is running and `REDIS_URL` in `.env` is correct; restart `propertyradarusa-celery` |
| PDF generation fails | Install WeasyPrint system deps: `libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev` |
| Unable to locate package python3.11 | The setup script now tries 3.11, 3.10, 3.9, then system python3. Re-copy the updated script and run again. Or install manually: `sudo apt-get update && sudo apt-get install -y python3.10 python3.10-venv python3.10-dev` and use Python 3.10 for the venv. |

---

## Summary

- Point **propertyradarusa.com** to **138.117.216.204**.
- Run **scripts/setup_server.sh** on the server with `MYSQL_ROOT_PASSWORD`, `APP_DIR`, `DOMAIN`, and `GITHUB_URL` set, or follow the manual steps above.
- Use **Nginx** for HTTPS and to serve the frontend and proxy `/api` to Gunicorn.
- Use **systemd** to run the API and Celery worker so they start on boot and restart on failure.
