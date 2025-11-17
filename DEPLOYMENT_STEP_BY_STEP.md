## Sew-Track production deployment (single VPS, two domains)

This guide sets up:
- Django app at subdomain: sewtrack.voris-art.com (Dockerized, proxied by host Nginx)
- Main site: voris-art.com (same server, separate directory)

Assumptions:
- OS: Ubuntu 22.04/24.04 on Contabo VPS (root or sudo access)
- Project path on server: /home/deploy/sew-track
- Docker/Compose used for app services; public traffic through host Nginx
- DNS managed at your registrar (create A records)

Adjust paths, users, and service names as needed.


### 1) DNS records

**⚠️ CRITICAL: DNS records MUST be created and propagated BEFORE running certbot!**

#### Step 1.1: Find your server's public IP

On your server, run:
```bash
curl -4 ifconfig.me
# or
hostname -I | awk '{print $1}'
# or check your VPS provider dashboard
```

Save this IP address - you'll need it for DNS records.

#### Step 1.2: Create A records at your domain registrar

Go to your domain registrar (where you bought `voris-art.com`) and create these DNS A records:

| Type | Name/Host | Value/Target | TTL |
|------|-----------|--------------|-----|
| A | sewtrack | YOUR_SERVER_IP | 3600 (or default) |
| A | @ | YOUR_SERVER_IP | 3600 (or default) |
| A | www | YOUR_SERVER_IP | 3600 (optional) |

**Note:** 
- For subdomain `sewtrack.voris-art.com`, the hostname is just `sewtrack` (not `sewtrack.voris-art.com`)
- For root domain `voris-art.com`, use `@` or leave the hostname field empty

#### Step 1.3: Verify DNS propagation

**Wait 5-15 minutes** for DNS to propagate, then verify:

```bash
# Check if DNS records exist
dig +short sewtrack.voris-art.com
dig +short voris-art.com

# Should return your server IP address
# If it returns nothing or wrong IP, DNS hasn't propagated yet

# Alternative check from your local machine:
nslookup sewtrack.voris-art.com
nslookup voris-art.com

# Or use online tools:
# https://dnschecker.org
# https://www.whatsmydns.net
```

**⚠️ DO NOT proceed to certbot until DNS resolves correctly!**

#### Troubleshooting DNS issues:

If DNS doesn't resolve after 30 minutes:
1. Double-check the A record values in your registrar's DNS panel
2. Verify you're using the correct server IP
3. Check for typos in the hostname (e.g., `sewtrack` not `sewtrack.voris-art.com`)
4. Some registrars require you to save/apply changes - make sure you clicked "Save"
5. Try using a different DNS checker tool to verify


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
ALLOWED_HOSTS=sewtrack.voris-art.com,voris-art.com
CSRF_TRUSTED_ORIGINS=https://sewtrack.voris-art.com,https://voris-art.com

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


### 10) Host-level Nginx for sewtrack.voris-art.com

**IMPORTANT:** First create HTTP-only config (without SSL), get certificates, then add SSL.

Create the initial HTTP-only vhost configuration:

```bash
sudo tee /etc/nginx/sites-available/sewtrack.voris-art.com >/dev/null << 'NGINX'
server {
    listen 80;
    server_name sewtrack.voris-art.com;

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

sudo ln -sf /etc/nginx/sites-available/sewtrack.voris-art.com /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```


### 11) Host-level Nginx for main site (voris-art.com)

Decide whether it’s a static site or another app. Example static root structure:

```bash
sudo mkdir -p /var/www/voris-art.com/current/public
echo 'Main site OK' | sudo tee /var/www/voris-art.com/current/public/index.html >/dev/null
```

Create HTTP-only vhost (SSL will be added after getting certificates):

```bash
sudo tee /etc/nginx/sites-available/voris-art.com >/dev/null << 'NGINX'
server {
    listen 80;
    server_name voris-art.com www.voris-art.com;

    root /var/www/voris-art.com/current/public;
    index index.html index.htm;

    # If you proxy to another app instead, replace with:
    # location / {
    #   proxy_pass http://127.0.0.1:PORT;
    #   proxy_set_header Host $host;
    #   proxy_set_header X-Real-IP $remote_addr;
    #   proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    #   proxy_set_header X-Forwarded-Proto $scheme;
    # }
}
NGINX

sudo ln -sf /etc/nginx/sites-available/voris-art.com /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```


### 12) Issue Let's Encrypt certificates

**⚠️ PREREQUISITE: DNS records must be created and propagated (see Step 1).**
**Verify DNS first:**
```bash
dig +short sewtrack.voris-art.com
# Must return your server IP, not empty!
```

**Method 1: Standalone mode (recommended for first-time setup)**

This method temporarily stops Nginx to get certificates:

```bash
sudo apt install -y certbot

# Verify DNS is working first!
dig +short sewtrack.voris-art.com
# If empty, DNS is not ready - go back to Step 1

# Stop nginx temporarily
sudo systemctl stop nginx

# Get certificates for sewtrack subdomain
sudo certbot certonly --standalone -d sewtrack.voris-art.com

# Get certificates for main domain
sudo certbot certonly --standalone -d voris-art.com -d www.voris-art.com

# Start nginx again
sudo systemctl start nginx
```

**Common certbot errors and solutions:**

- **"DNS problem: NXDOMAIN"** → DNS records don't exist or haven't propagated. Go back to Step 1.
- **"Failed to download challenge files"** → Firewall blocking port 80, or DNS not pointing to this server.
- **"Connection refused"** → Nginx or another service is using port 80. Make sure `systemctl stop nginx` worked.

**Method 2: Using nginx plugin (after HTTP configs are working)**

If you prefer the nginx plugin, make sure your HTTP configs work first, then:

```bash
sudo apt install -y certbot python3-certbot-nginx

# This will automatically update your nginx configs with SSL
sudo certbot --nginx -d sewtrack.voris-art.com
sudo certbot --nginx -d voris-art.com -d www.voris-art.com
```

**After getting certificates, update nginx configs to use SSL:**

For sewtrack.voris-art.com:

```bash
sudo tee /etc/nginx/sites-available/sewtrack.voris-art.com >/dev/null << 'NGINX'
server {
    listen 80;
    server_name sewtrack.voris-art.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name sewtrack.voris-art.com;

    ssl_certificate /etc/letsencrypt/live/sewtrack.voris-art.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/sewtrack.voris-art.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers off;
    add_header Strict-Transport-Security "max-age=63072000" always;

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
```

For voris-art.com:

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
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers off;
    add_header Strict-Transport-Security "max-age=63072000" always;

    root /var/www/voris-art.com/current/public;
    index index.html index.htm;

    # If you proxy to another app instead, replace with location / { proxy_pass ... }
}
NGINX
```

Reload nginx:

```bash
sudo nginx -t && sudo systemctl reload nginx
```

**Troubleshooting: If you see "Welcome to nginx!" or "Main site OK" instead of your Django app:**

1. **Check if Django container is running:**
```bash
cd /home/deploy/sew-track
docker compose -f docker-compose.production.yml ps
# web container should be "Up" and healthy
```

2. **Check if Django is accessible on port 8000:**
```bash
curl http://127.0.0.1:8000
# Should return Django response, not "Connection refused"
```

3. **Verify Nginx configuration is active and correct:**
```bash
# Check which configs are enabled
ls -la /etc/nginx/sites-enabled/

# Check if default config is interfering
sudo ls -la /etc/nginx/sites-enabled/ | grep default
# If default exists, disable it:
sudo rm -f /etc/nginx/sites-enabled/default

# Verify sewtrack config exists and is enabled
sudo ls -la /etc/nginx/sites-available/sewtrack.voris-art.com
sudo ls -la /etc/nginx/sites-enabled/sewtrack.voris-art.com

# Check the actual config content
sudo cat /etc/nginx/sites-available/sewtrack.voris-art.com
# Should show server_name sewtrack.voris-art.com and proxy_pass to http://127.0.0.1:8000
```

4. **IMPORTANT: Check if main site config is interfering:**
```bash
# Check voris-art.com config
sudo cat /etc/nginx/sites-available/voris-art.com | grep server_name
# Should only show: server_name voris-art.com www.voris-art.com;
# If it shows sewtrack.voris-art.com, that's the problem!

# Verify server_name specificity - sewtrack config should be checked FIRST
sudo nginx -T | grep -A 5 "server_name.*sewtrack"
```

5. **Check Nginx error and access logs:**
```bash
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

6. **Test Nginx configuration and reload:**
```bash
sudo nginx -t
# If test passes:
sudo systemctl reload nginx
```

7. **If still showing wrong content, check Nginx config priority:**
```bash
# Nginx uses first matching server_name, so order matters
# Make sure sewtrack config is loaded before voris-art config
# You can rename configs to control load order (alphabetical):
# sewtrack.voris-art.com loads before voris-art.com
```

**Common issue: "Main site OK" appears instead of Django app**

This means Nginx is using the `voris-art.com` config instead of `sewtrack.voris-art.com`. Fix:

```bash
# 1. Make sure sewtrack config exists and is correct
sudo cat /etc/nginx/sites-available/sewtrack.voris-art.com

# 2. Ensure it's enabled
sudo ln -sf /etc/nginx/sites-available/sewtrack.voris-art.com /etc/nginx/sites-enabled/

# 3. Verify server_name in voris-art.com config does NOT include sewtrack
sudo grep server_name /etc/nginx/sites-available/voris-art.com
# Should only show: voris-art.com www.voris-art.com

# 4. Test and reload
sudo nginx -t && sudo systemctl reload nginx
```

**Set up auto-renewal:**

```bash
sudo systemctl enable --now certbot.timer
sudo certbot renew --dry-run
```

**Note:** If you used standalone mode, you may need to configure certbot renewal hooks to stop/start nginx. The nginx plugin handles this automatically.

### 13) Manage Docker Compose with systemd

Keep the Docker Compose stack running after reboots by supervising it with systemd.

1. **Create the unit file:**

```bash
sudo tee /etc/systemd/system/sewtrack.service >/dev/null <<'SERVICE'
[Unit]
Description=Sew-Track production stack (Docker Compose)
Requires=docker.service
After=docker.service network-online.target

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/deploy/sew-track
Environment="ENV_FILE=/home/deploy/sew-track/.env.production"
ExecStart=/usr/bin/env bash -c 'set -a; source "$ENV_FILE"; docker compose -f docker-compose.production.yml up -d'
ExecStop=/usr/bin/env bash -c 'set -a; source "$ENV_FILE"; docker compose -f docker-compose.production.yml down'
ExecReload=/usr/bin/env bash -c 'set -a; source "$ENV_FILE"; docker compose -f docker-compose.production.yml up -d --build --remove-orphans'
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
SERVICE
```

2. **Reload systemd and enable the service:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now sewtrack.service
```

3. **Everyday commands:**

```bash
# Check service status
sudo systemctl status sewtrack.service

# Restart stack after code/env changes
sudo systemctl restart sewtrack.service

# View unit logs (application logs stay available via docker compose logs)
journalctl -u sewtrack.service -f
```

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

- **DNS not resolving (NXDOMAIN)**: Most common issue! DNS A records must be created at registrar BEFORE running certbot. Wait 5-15 minutes for propagation, verify with `dig +short sewtrack.voris-art.com`.
- **Certbot fails with DNS errors**: Always verify DNS propagation first. Use `dig`, `nslookup`, or online DNS checkers.
- **Pillow build fails**: ensure Dockerfile installs zlib1g-dev and related libs, or use python:3.12-slim.
- **Redis unhealthy**: healthcheck must authenticate when --requirepass is set (see step 7).
- **502/504 from Nginx**: verify `web` is bound on 127.0.0.1:8000 and container is healthy; check ALLOWED_HOSTS/CSRF_TRUSTED_ORIGINS.
- **Permissions on static/media**: ensure the `web` container writes to mounted paths and Nginx aliases match host paths.


