## Sew-Track production deployment (single VPS, two domains)

This guide sets up:
- Django app at subdomain: sewtrack.voris-atr.com (Dockerized, proxied by host Nginx)
- Main site: voris-art.com (same server, separate directory)

Assumptions:
- OS: Ubuntu 22.04/24.04 on Contabo VPS (root or sudo access)
- Project path on server: /home/deploy/sew-track
- Docker/Compose used for app services; public traffic through host Nginx
- DNS managed at your registrar (create A records)

Adjust paths, users, and service names as needed.


### 1) DNS records

Create A records pointing to your VPS public IP:
- sewtrack.voris-atr.com → YOUR_SERVER_IP
- voris-art.com → YOUR_SERVER_IP
- www.voris-art.com → YOUR_SERVER_IP (optional)

Verify propagation:

```bash
dig +short sewtrack.voris-atr.com
dig +short voris-art.com
```


### 2) Server prerequisites

```bash
sudo apt update
sudo apt install -y \
  ca-certificates curl gnupg lsb-release \
  ufw git nginx

# Firewall (optional but recommended)
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable
```


### 3) Install Docker and Compose plugin

```bash
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo $VERSION_CODENAME) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

sudo systemctl enable --now docker
```


### 4) Get the project onto the server

```bash
sudo mkdir -p /home/deploy
sudo chown -R $USER:$USER /home/deploy
cd /home/deploy

# If not already present on server:
git clone <YOUR_REPO_URL> sew-track
cd sew-track
```


### 5) Prepare environment variables

Create a .env.production file in the project root (same dir as docker-compose.production.yml).

```bash
cat > .env.production << 'EOF'
SECRET_KEY=change_me
DEBUG=False
ALLOWED_HOSTS=sewtrack.voris-atr.com,voris-art.com
CSRF_TRUSTED_ORIGINS=https://sewtrack.voris-atr.com,https://voris-art.com

DB_NAME=sewtrack_db
DB_USER=postgres
DB_PASSWORD=strong_db_password

REDIS_PASSWORD=strong_redis_password

FLOWER_USER=admin
FLOWER_PASSWORD=admin

# Optional: Sentry DSN etc.
EOF
```

When running Compose commands, export the env file:

```bash
export $(grep -v '^#' .env.production | xargs) || true
```


### 6) Update Dockerfile to build Pillow on slim base (or use Python 3.12)

If you keep python:3.14-slim, add system libs so Pillow compiles:

```Dockerfile
RUN apt-get update && apt-get install -y \
    gcc postgresql-client libpq-dev \
    zlib1g-dev libjpeg-dev libpng-dev libopenjp2-7-dev libtiff-dev \
 && apt-get clean && rm -rf /var/lib/apt/lists/*
```

Alternatively, switch to python:3.12-slim to use prebuilt wheels and avoid compiling.


### 7) Fix Redis healthcheck with password

In docker-compose.production.yml ensure the Redis healthcheck authenticates when --requirepass is set:

```yaml
redis:
  image: redis:7-alpine
  command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD:-}
  healthcheck:
    test: ["CMD", "redis-cli", "-a", "$${REDIS_PASSWORD}", "ping"]
    interval: 10s
    timeout: 3s
    retries: 5
```

Note the escaped $${REDIS_PASSWORD} so Compose passes the value inside the container.


### 8) Bind Django container only to localhost

We’ll serve traffic via host Nginx. Bind the Django container to 127.0.0.1 only:

```yaml
web:
  ports:
    - "127.0.0.1:8000:8000"
```

You can remove the containerized nginx service from the compose file, since we’re using host Nginx.


### 9) Build and start core services

```bash
docker compose -f docker-compose.production.yml build --no-cache
docker compose -f docker-compose.production.yml up -d db redis
docker compose -f docker-compose.production.yml ps
# Wait until db and redis are Healthy

docker compose -f docker-compose.production.yml up -d web
docker compose -f docker-compose.production.yml exec web python manage.py migrate
docker compose -f docker-compose.production.yml exec web python manage.py collectstatic --noinput

# (Optional) start workers
docker compose -f docker-compose.production.yml up -d celery_worker celery_beat
```


### 10) Host-level Nginx for sewtrack.voris-atr.com

Create the vhost configuration:

```bash
sudo tee /etc/nginx/sites-available/sewtrack.voris-atr.com >/dev/null << 'NGINX'
server {
    listen 80;
    server_name sewtrack.voris-atr.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name sewtrack.voris-atr.com;

    ssl_certificate /etc/letsencrypt/live/sewtrack.voris-atr.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/sewtrack.voris-atr.com/privkey.pem;

    client_max_body_size 100M;

    location /static/ {
        alias /home/deploy/sew-track/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /home/deploy/sew-track/media/;
        expires 7d;
        add_header Cache-Control "public";
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 60s;
    }
}
NGINX

sudo ln -sf /etc/nginx/sites-available/sewtrack.voris-atr.com /etc/nginx/sites-enabled/
```


### 11) Host-level Nginx for main site (voris-art.com)

Decide whether it’s a static site or another app. Example static root structure:

```bash
sudo mkdir -p /var/www/voris-art.com/current/public
echo 'Main site OK' | sudo tee /var/www/voris-art.com/current/public/index.html >/dev/null
```

Create vhost:

```bash
sudo tee /etc/nginx/sites-available/voris-art.com >/dev/null << 'NGINX'
server {
    listen 80;
    server_name voris-art.com www.voris-art.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name voris-art.com www.voris-art.com;

    ssl_certificate /etc/letsencrypt/live/voris-art.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/voris-art.com/privkey.pem;

    root /var/www/voris-art.com/current/public;
    index index.html index.htm;

    # If you proxy to another app instead, replace with a location / { proxy_pass ... }
}
NGINX

sudo ln -sf /etc/nginx/sites-available/voris-art.com /etc/nginx/sites-enabled/
```


### 12) Issue Let’s Encrypt certificates

Use the nginx plugin so Certbot can edit TLS automatically:

```bash
sudo apt install -y certbot python3-certbot-nginx

sudo certbot --nginx -d sewtrack.voris-atr.com
sudo certbot --nginx -d voris-art.com -d www.voris-art.com

# Verify and set up auto-renew
sudo systemctl enable --now certbot.timer
sudo certbot renew --dry-run
```

If you prefer standalone mode, temporarily stop Nginx and run certonly:

```bash
sudo systemctl stop nginx
sudo certbot certonly --standalone -d sewtrack.voris-atr.com
sudo certbot certonly --standalone -d voris-art.com -d www.voris-art.com
sudo systemctl start nginx
```


### 13) Reload Nginx

```bash
sudo nginx -t && sudo systemctl reload nginx
```

Check both domains over HTTPS in your browser.


### 14) Post-deploy maintenance

- Update repo and redeploy:

```bash
cd /home/deploy/sew-track
git pull
export $(grep -v '^#' .env.production | xargs) || true
docker compose -f docker-compose.production.yml build
docker compose -f docker-compose.production.yml up -d
docker compose -f docker-compose.production.yml exec web python manage.py migrate
docker compose -f docker-compose.production.yml exec web python manage.py collectstatic --noinput
sudo nginx -t && sudo systemctl reload nginx
```

- Logs:

```bash
docker compose -f docker-compose.production.yml logs -f web
docker compose -f docker-compose.production.yml logs -f celery_worker
sudo journalctl -u nginx -f
```

- Backups: snapshot Postgres volume and media directory periodically.


### 15) Common pitfalls

- Pillow build fails: ensure Dockerfile installs zlib1g-dev and related libs, or use python:3.12-slim.
- Redis unhealthy: healthcheck must authenticate when --requirepass is set (see step 7).
- 502/504 from Nginx: verify `web` is bound on 127.0.0.1:8000 and container is healthy; check ALLOWED_HOSTS/CSRF_TRUSTED_ORIGINS.
- Permissions on static/media: ensure the `web` container writes to mounted paths and Nginx aliases match host paths.


