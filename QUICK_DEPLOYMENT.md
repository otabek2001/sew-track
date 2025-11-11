# ⚡ SEW-TRACK - Quick Deployment (15 daqiqada)

Tez va oddiy deployment yo'riqnomasi. Batafsil ma'lumot uchun `DEPLOYMENT_GUIDE.md` ga qarang.

---

## 🎯 **Prerequisites**

1. ✅ VPS Server (Ubuntu 22.04, 2GB RAM minimum)
2. ✅ Domain (optional, IP bilan ham ishlaydi)
3. ✅ SSH access

---

## 🚀 **5 Qadam - Production Deploy**

### **1️⃣ Server tayyorlash (5 min)**

```bash
# Server ga SSH orqali ulanish
ssh root@your_server_ip

# Docker o'rnatish
curl -fsSL https://get.docker.com | sh

# Firewall sozlash
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable

# Deploy user yaratish
adduser deploy
usermod -aG sudo,docker deploy
su - deploy
```

### **2️⃣ Loyihani clone qilish (2 min)**

```bash
# Repository clone
cd ~
git clone https://github.com/yourusername/sew-track.git
cd sew-track
```

### **3️⃣ Environment sozlash (3 min)**

```bash
# .env yaratish
cp .env.example .env
nano .env
```

**Minimal .env (development test uchun):**

```bash
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
DJANGO_SETTINGS_MODULE=config.settings.production
DEBUG=False
ALLOWED_HOSTS=your_server_ip,localhost

DB_NAME=sewtrack_db
DB_USER=postgres
DB_PASSWORD=strongPassword123!
DB_HOST=db
DB_PORT=5432

REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0

SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
```

### **4️⃣ Docker bilan ishga tushirish (3 min)**

```bash
# Build va start
docker compose -f docker-compose.production.yml up -d --build

# Migration
docker compose -f docker-compose.production.yml exec web python manage.py migrate

# Static files
docker compose -f docker-compose.production.yml exec web python manage.py collectstatic --noinput

# Superuser yaratish
docker compose -f docker-compose.production.yml exec web python manage.py createsuperuser

# Demo data (optional)
docker compose -f docker-compose.production.yml exec web python manage.py shell < scripts/create_demo_data.py
```

### **5️⃣ Test qilish (2 min)**

```bash
# Browser da ochish
http://your_server_ip

# Yoki curl bilan
curl http://your_server_ip

# Logs tekshirish
docker compose -f docker-compose.production.yml logs -f web
```

---

## ✅ **Tayyor!**

Tizim ishga tushdi:

- **Login:** `http://your_server_ip/login/`
- **Admin:** `http://your_server_ip/admin/`
- **API:** `http://your_server_ip/api/v1/`
- **Flower:** `http://your_server_ip:5555/`

---

## 🔐 **SSL qo'shish (optional, +10 min)**

```bash
# Domain sozlash (DNS)
# A record: @ -> your_server_ip

# Certbot o'rnatish
sudo apt install -y certbot

# SSL olish
docker compose -f docker-compose.production.yml stop nginx
sudo certbot certonly --standalone -d your-domain.com
sudo cp /etc/letsencrypt/live/your-domain.com/*.pem ~/sew-track/nginx/ssl/
docker compose -f docker-compose.production.yml start nginx

# .env da SSL yoqish
nano .env
# SECURE_SSL_REDIRECT=True
# SESSION_COOKIE_SECURE=True
# CSRF_COOKIE_SECURE=True

# Restart
docker compose -f docker-compose.production.yml restart web
```

---

## 🛠️ **Foydali Buyruqlar**

### Status tekshirish:
```bash
docker compose -f docker-compose.production.yml ps
```

### Logs ko'rish:
```bash
docker compose -f docker-compose.production.yml logs -f
```

### Restart:
```bash
docker compose -f docker-compose.production.yml restart
```

### Stop:
```bash
docker compose -f docker-compose.production.yml down
```

### Update (yangi code):
```bash
git pull
docker compose -f docker-compose.production.yml up -d --build
docker compose -f docker-compose.production.yml exec web python manage.py migrate
docker compose -f docker-compose.production.yml exec web python manage.py collectstatic --noinput
```

### Backup:
```bash
# Database
docker compose -f docker-compose.production.yml exec db pg_dump -U postgres sewtrack_db > backup.sql

# Media files
tar -czf media_backup.tar.gz media/
```

---

## 🆘 **Troubleshooting**

### Container ishlamayapti:
```bash
docker compose -f docker-compose.production.yml logs <service_name>
docker compose -f docker-compose.production.yml restart <service_name>
```

### Database xatosi:
```bash
# Database logs
docker compose -f docker-compose.production.yml logs db

# Database shell
docker compose -f docker-compose.production.yml exec db psql -U postgres sewtrack_db
```

### Static files 404:
```bash
docker compose -f docker-compose.production.yml exec web python manage.py collectstatic --noinput
docker compose -f docker-compose.production.yml restart nginx
```

---

## 📚 **Keyingi qadamlar**

1. ✅ **Full deployment guide:** `DEPLOYMENT_GUIDE.md`
2. ✅ **Production checklist:** `PRODUCTION_CHECKLIST.md`
3. ✅ **Security:** SSL, Firewall, Backups
4. ✅ **Monitoring:** Logs, Flower, Uptime
5. ✅ **Optimization:** Caching, Database tuning

---

## 🎉 **Tayyor!**

15 daqiqada SEW-TRACK production serverda ishlamoqda! 🚀

**Test:** `http://your_server_ip/login/`

---

**Version:** 1.0.0  
**Created:** November 11, 2024

