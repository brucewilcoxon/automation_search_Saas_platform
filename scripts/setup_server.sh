#!/bin/bash
# Setup Property Radar USA (Auction Navigator Suite) on Ubuntu 20.04
# Usage: export APP_DIR=... DOMAIN=... GITHUB_URL=... && sudo -E bash /tmp/setup_server.sh
# If you see errors like $'\r': command not found, run first: sed -i 's/\r$//' /tmp/setup_server.sh

# Fix Windows CRLF line endings if present (re-run self after fixing)
if grep -q $'\r' "$0" 2>/dev/null; then
  sed -i 's/\r$//' "$0"
  exec bash "$0" "$@"
fi

set -e

# Install only packages that are not already installed (skips if all present)
apt_install_if_missing() {
  local to_install=()
  for pkg in "$@"; do
    dpkg -s "$pkg" &>/dev/null || to_install+=("$pkg")
  done
  if [ ${#to_install[@]} -gt 0 ]; then
    apt-get install -y "${to_install[@]}"
  else
    echo ">>> All requested packages already installed: $*"
  fi
}

# --- Config (override with environment variables) ---
APP_DIR="${APP_DIR:-/var/www/propertyradarusa}"
DOMAIN="${DOMAIN:-propertyradarusa.com}"
GITHUB_URL="${GITHUB_URL:-https://github.com/brucewilcoxon/automation_search_Saas_platform.git}"
DB_NAME="${DB_NAME:-auction_navigator}"
DB_USER="${DB_USER:-pradar}"
RUN_CERTBOT="${RUN_CERTBOT:-no}"  # set to "yes" to run certbot (DNS must point to this server)

echo "=== Property Radar USA - Server setup ==="
echo "APP_DIR=$APP_DIR"
echo "DOMAIN=$DOMAIN"
echo "GITHUB_URL=$GITHUB_URL"
echo "DB_NAME=$DB_NAME"
echo "DB_USER=$DB_USER"
echo ""

# Generate a random password for the app DB user (saved to .env)
DB_PASSWORD="${DB_PASSWORD:-$(openssl rand -base64 24)}"
echo "Database user '${DB_USER}' password will be written to .env (first 4 chars: ${DB_PASSWORD:0:4}***)"

# --- System packages ---
echo ">>> Updating system and installing packages..."
apt-get update -y
apt_install_if_missing software-properties-common curl build-essential git

# Python 3.9+ (prefer 3.11, then 3.10, then 3.9; fallback to system 3.8)
PYTHON_BIN=""
for ver in 3.11 3.10 3.9; do
  if command -v python${ver} >/dev/null 2>&1; then
    PYTHON_BIN="python${ver}"
    echo ">>> Using existing $PYTHON_BIN"
    break
  fi
done
if [ -z "$PYTHON_BIN" ]; then
  add-apt-repository -y ppa:deadsnakes/ppa
  apt-get update -y
  for ver in 3.11 3.10 3.9; do
    apt_install_if_missing python${ver} python${ver}-venv python${ver}-dev 2>/dev/null || true
    if command -v python${ver} >/dev/null 2>&1; then
      PYTHON_BIN="python${ver}"
      echo ">>> Using $PYTHON_BIN"
      break
    fi
  done
fi
if [ -z "$PYTHON_BIN" ]; then
  apt_install_if_missing python3 python3-venv python3-dev
  PYTHON_BIN="python3"
  echo ">>> Using system $PYTHON_BIN"
fi
command -v "$PYTHON_BIN" >/dev/null || { echo "No suitable Python found."; exit 1; }

# Node.js 18+
if command -v node &>/dev/null && [ "$(node -v | cut -d. -f1 | tr -d v)" -ge 18 ] 2>/dev/null; then
  echo ">>> Node.js $(node -v) already installed"
else
  curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
  apt_install_if_missing nodejs
fi

# MySQL 8
apt_install_if_missing mysql-server
systemctl start mysql || true
systemctl enable mysql || true

# Redis
apt_install_if_missing redis-server
systemctl start redis-server || true
systemctl enable redis-server || true

# Nginx
apt_install_if_missing nginx

# WeasyPrint / PDF dependencies
apt_install_if_missing libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info

# --- Database ---
echo ">>> Creating database and user..."
# Use mysql as root (no password) or sudo mysql (auth_socket on Ubuntu)
mysql -u root -e "
  CREATE DATABASE IF NOT EXISTS ${DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
  DROP USER IF EXISTS '${DB_USER}'@'localhost';
  CREATE USER '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASSWORD}';
  GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${DB_USER}'@'localhost';
  FLUSH PRIVILEGES;
" 2>/dev/null || sudo mysql -e "
  CREATE DATABASE IF NOT EXISTS ${DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
  DROP USER IF EXISTS '${DB_USER}'@'localhost';
  CREATE USER '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASSWORD}';
  GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${DB_USER}'@'localhost';
  FLUSH PRIVILEGES;
"
DATABASE_URL="mysql+pymysql://${DB_USER}:${DB_PASSWORD}@127.0.0.1:3306/${DB_NAME}?charset=utf8mb4"

# --- App directory and clone ---
echo ">>> Cloning repository to $APP_DIR..."
mkdir -p "$(dirname "$APP_DIR")"
if [ -d "$APP_DIR/.git" ]; then
  cd "$APP_DIR" && git pull && cd -
else
  git clone "$GITHUB_URL" "$APP_DIR"
fi
cd "$APP_DIR"

# --- Python venv and dependencies ---
echo ">>> Setting up Python virtual environment..."
$PYTHON_BIN -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

# --- .env ---
echo ">>> Creating .env..."
cat > .env <<ENVFILE
DATABASE_URL=${DATABASE_URL}
REDIS_URL=redis://127.0.0.1:6379/0
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
CORS_ORIGINS=["https://${DOMAIN}","https://www.${DOMAIN}"]
ENVFILE

# --- Migrations ---
echo ">>> Running database migrations..."
export PYTHONPATH="$APP_DIR"
./venv/bin/alembic -c backend/db/alembic.ini upgrade head

# --- Frontend build ---
echo ">>> Building frontend..."
cd frontend
npm ci
npm run build
cd "$APP_DIR"

# --- Nginx ---
echo ">>> Configuring Nginx..."
cat > /etc/nginx/sites-available/propertyradarusa <<NGINX
server {
    listen 80;
    server_name ${DOMAIN} www.${DOMAIN};
    root ${APP_DIR}/frontend/dist;
    index index.html;

    location / {
        try_files \$uri \$uri/ /index.html;
    }

    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /health {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
    }
}
NGINX
ln -sf /etc/nginx/sites-available/propertyradarusa /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

# --- Systemd: API ---
echo ">>> Creating systemd service: propertyradarusa-api..."
cat > /etc/systemd/system/propertyradarusa-api.service <<SVC
[Unit]
Description=Property Radar USA API (Gunicorn)
After=network.target mysql.service redis-server.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=${APP_DIR}
Environment="PATH=${APP_DIR}/venv/bin"
EnvironmentFile=${APP_DIR}/.env
ExecStart=${APP_DIR}/venv/bin/gunicorn backend.app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 127.0.0.1:8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
SVC

# --- Systemd: Celery ---
echo ">>> Creating systemd service: propertyradarusa-celery..."
cat > /etc/systemd/system/propertyradarusa-celery.service <<SVC
[Unit]
Description=Property Radar USA Celery Worker
After=network.target mysql.service redis-server.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=${APP_DIR}
Environment="PATH=${APP_DIR}/venv/bin"
EnvironmentFile=${APP_DIR}/.env
ExecStart=${APP_DIR}/venv/bin/celery -A workers.celery_app worker --loglevel=info
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
SVC

# --- Permissions ---
echo ">>> Setting ownership to www-data..."
chown -R www-data:www-data "$APP_DIR"
chmod 600 "$APP_DIR/.env"

# --- Enable and start services ---
systemctl daemon-reload
systemctl enable propertyradarusa-api propertyradarusa-celery
systemctl restart propertyradarusa-api propertyradarusa-celery

# --- SSL (optional) ---
if [ "$RUN_CERTBOT" = "yes" ]; then
  echo ">>> Running Certbot for SSL..."
  apt_install_if_missing certbot python3-certbot-nginx
  certbot --nginx -d "$DOMAIN" -d "www.$DOMAIN" --non-interactive --agree-tos --register-unsafely-without-email || true
fi

echo ""
echo "=== Setup complete ==="
echo "App root: $APP_DIR"
echo "Domain: $DOMAIN"
echo "API: http://127.0.0.1:8000 (proxied via Nginx at /api)"
echo ""
echo "Check status:"
echo "  sudo systemctl status propertyradarusa-api propertyradarusa-celery nginx"
echo ""
echo "To enable HTTPS later, run:"
echo "  sudo certbot --nginx -d ${DOMAIN} -d www.${DOMAIN}"
echo ""
echo "Database user: $DB_USER  (password was written to $APP_DIR/.env)"
