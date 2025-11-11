# 🚀 SEW-TRACK - Production Deployment Guide

Bu qo'llanma SEW-TRACK tizimini production serverga deploy qilish bo'yicha to'liq yo'riqnoma.

---

## 📋 **Kirish**

**Deployment variantlari:**
1. **VPS/Cloud Server** (DigitalOcean, AWS, Hetzner) - **TAVSIYA ETILADI** ⭐
2. **Heroku** (Tezkor, lekin cheklangan)
3. **Railway** (Modern, oson)

Bu qo'llanmada **VPS (DigitalOcean)** orqali deploy qilamiz - eng moslashuvchan va professional yechim.

---

## 🎯 **Server Talablari**

### **Minimum:**
- **CPU:** 2 cores
- **RAM:** 2GB
- **Disk:** 20GB SSD
- **OS:** Ubuntu 22.04 LTS
- **Network:** 1Gbps

### **Tavsiya etilgan (100+ foydalanuvchi):**
- **CPU:** 4 cores
- **RAM:** 4GB
- **Disk:** 40GB SSD
- **OS:** Ubuntu 22.04 LTS

### **Narx (taxminan):**
- DigitalOcean: $12-24/oy
- AWS Lightsail: $10-20/oy
- Hetzner: €4-12/oy

---

## 📦 **1-QADIM: VPS Server Sozlash**

### 1.1. DigitalOcean Droplet yaratish

1. **https://digitalocean.com** ga kiring (yoki ro'yxatdan o'ting)
2. **Create** → **Droplets** ni tanlang
3. Quyidagi sozlamalarni tanlang:
   - **Image:** Ubuntu 22.04 (LTS) x64
   - **Plan:** Basic
   - **CPU:** Regular - 2GB RAM / 1 CPU ($12/mo)
   - **Datacenter:** Frankfurt yoki Amsterdam (Uzbekiston uchun eng yaqin)
   - **Authentication:** SSH Key (yoki Password)
   - **Hostname:** sewtrack-production

4. **Create Droplet** ni bosing

5. 1-2 daqiqada server tayyor bo'ladi va sizga IP address beriladi.

### 1.2. SSH orqali serverga ulanish

```bash
# IP manzilni o'zgartiring
ssh root@your_server_ip

# Agar SSH key bilan ulansangiz:
ssh -i ~/.ssh/id_rsa root@your_server_ip
```

---

## 🔧 **2-QADAM: Server Tayyorlash**

### 2.1. Tizimni yangilash

```bash
# Update package lists
apt update && apt upgrade -y

# Install essential packages
apt install -y \
    git \
    curl \
    wget \
    vim \
    htop \
    ufw \
    build-essential \
    libpq-dev \
    python3-dev \
    python3-pip \
    python3-venv
```

### 2.2. Docker o'rnatish

```bash
# Docker o'rnatish (official script)
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Docker Compose o'rnatish
apt install -y docker-compose-plugin

# Docker servisini yoqish
systemctl enable docker
systemctl start docker

# Tekshirish
docker --version
docker compose version
```

### 2.3. Firewall sozlash

```bash
# UFW (Uncomplicated Firewall) yoqish
ufw allow OpenSSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw enable

# Status tekshirish
ufw status
```

### 2.4. Non-root user yaratish (xavfsizlik)

```bash
# Yangi user yaratish
adduser deploy
usermod -aG sudo deploy
usermod -aG docker deploy

# SSH key nusxalash (agar ishlatayotgan bo'lsangiz)
rsync --archive --chown=deploy:deploy ~/.ssh /home/deploy

# Yangi userga o'tish
su - deploy
```

---

## 📥 **3-QADAM: Loyihani Serverga Ko'chirish**

### 3.1. Git repository clone qilish

```bash
# Home directoriga o'tish
cd ~

# Repository clone qilish
git clone https://github.com/yourusername/sew-track.git
cd sew-track

# Production branchga o'tish (agar bor bo'lsa)
git checkout production
```

### 3.2. Environment variables sozlash

```bash
# .env faylini yaratish
cp .env.example .env

# .env faylini tahrirlash
nano .env
```

**.env fayl mazmuni (production):**

```bash
# Django Settings
SECRET_KEY=your-very-long-random-secret-key-here-generate-new-one
DJANGO_SETTINGS_MODULE=config.settings.production
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,your_server_ip

# Database
DB_NAME=sewtrack_db
DB_USER=postgres
DB_PASSWORD=create-strong-password-here-min-16-chars
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=django-db

# CORS
CORS_ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com

# Security (SSL uchun)
SECURE_SSL_REDIRECT=False  # Boshida False, SSL sozlanganidan keyin True
SESSION_COOKIE_SECURE=False  # SSL bilan True
CSRF_COOKIE_SECURE=False  # SSL bilan True

# Flower (Celery monitoring)
FLOWER_USER=admin
FLOWER_PASSWORD=create-secure-password-here
```

**SECRET_KEY generatsiya qilish:**

```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## 🐳 **4-QADAM: Docker bilan Deployment**

### 4.1. Docker images yaratish

```bash
cd ~/sew-track

# Production image build qilish
docker compose -f docker-compose.production.yml build
```

### 4.2. Containerlarni ishga tushirish

```bash
# Barcha servislarni background da ishga tushirish
docker compose -f docker-compose.production.yml up -d

# Loglarni kuzatish
docker compose -f docker-compose.production.yml logs -f
```

### 4.3. Database migration va static files

```bash
# Database migratsiyalarini qo'llash
docker compose -f docker-compose.production.yml exec web python manage.py migrate

# Static files yig'ish
docker compose -f docker-compose.production.yml exec web python manage.py collectstatic --noinput

# Superuser yaratish
docker compose -f docker-compose.production.yml exec web python manage.py createsuperuser
```

### 4.4. Test ma'lumotlarini yuklash (demo uchun)

```bash
# Test datani yuklash
docker compose -f docker-compose.production.yml exec web python manage.py shell < scripts/create_demo_data.py
```

### 4.5. Servislar holatini tekshirish

```bash
# Barcha containerlar ishlaydimi?
docker compose -f docker-compose.production.yml ps

# Loglarni ko'rish
docker compose -f docker-compose.production.yml logs web
docker compose -f docker-compose.production.yml logs db
docker compose -f docker-compose.production.yml logs celery_worker
```

---

## 🌐 **5-QADAM: Domain va SSL Sozlash**

### 5.1. Domain sozlash

1. **Domain registrar** (Namecheap, GoDaddy) ga kiring
2. **DNS Settings** ga o'ting
3. **A Record** qo'shing:
   ```
   Type: A
   Host: @
   Value: your_server_ip
   TTL: 3600
   ```
4. **www subdomain** uchun:
   ```
   Type: A
   Host: www
   Value: your_server_ip
   TTL: 3600
   ```

5. DNS propagatsiyani tekshiring (5-30 daqiqa):
   ```bash
   dig your-domain.com
   ```

### 5.2. Let's Encrypt SSL o'rnatish

**Certbot o'rnatish:**

```bash
# Serverda (deploy user sifatida)
sudo apt install -y certbot python3-certbot-nginx
```

**SSL sertifikat olish:**

```bash
# Nginx containerdan tashqarida certbot ishlatamiz
# Vaqtincha nginx containerini to'xtatamiz
docker compose -f docker-compose.production.yml stop nginx

# Certbot bilan SSL olish
sudo certbot certonly --standalone -d your-domain.com -d www.your-domain.com

# SSL fayllarini nginx papkaga nusxalash
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ~/sew-track/nginx/ssl/
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ~/sew-track/nginx/ssl/
sudo chown deploy:deploy ~/sew-track/nginx/ssl/*

# Nginx ni qayta ishga tushirish
docker compose -f docker-compose.production.yml start nginx
```

**Nginx configuration (SSL):**

`nginx/conf.d/sewtrack.conf` faylini tahrirlang va SSL qismini uncomment qiling:

```bash
nano ~/sew-track/nginx/conf.d/sewtrack.conf
```

SSL server block'ini yoqing va HTTP redirectni uncomment qiling.

**Nginx reload:**

```bash
docker compose -f docker-compose.production.yml restart nginx
```

### 5.3. Auto-renewal sozlash

```bash
# Cron job qo'shish (SSL auto-renewal)
sudo crontab -e

# Quyidagini qo'shing (har kuni soat 2 da tekshiradi):
0 2 * * * certbot renew --quiet --post-hook "cp /etc/letsencrypt/live/your-domain.com/*.pem /home/deploy/sew-track/nginx/ssl/ && cd /home/deploy/sew-track && docker compose -f docker-compose.production.yml restart nginx"
```

### 5.4. .env faylida SSL yoqish

```bash
nano ~/sew-track/.env

# O'zgartiring:
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

**Django containerini restart qiling:**

```bash
docker compose -f docker-compose.production.yml restart web
```

---

## 🔐 **6-QADAM: Xavfsizlik Sozlamalari**

### 6.1. Database parolini mustahkamlash

```bash
# .env faylida kuchli parol yarating
# Kamida 16 belgi, harflar, raqamlar, maxsus belgilar

# Database containerini restart qiling
docker compose -f docker-compose.production.yml restart db
```

### 6.2. Firewall qo'shimcha qoidalar

```bash
# Faqat kerakli portlarni ochish
sudo ufw status numbered

# Agar qo'shimcha portlar ochiq bo'lsa, yoping
# sudo ufw delete <rule_number>
```

### 6.3. Fail2ban o'rnatish (brute-force xujumlardan himoya)

```bash
sudo apt install -y fail2ban

# Fail2ban sozlash
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 6.4. Regular backups sozlash

**Backup script yaratish:**

```bash
nano ~/backup.sh
```

**backup.sh mazmuni:**

```bash
#!/bin/bash
BACKUP_DIR="/home/deploy/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="sewtrack_db"
DB_USER="postgres"

# Backup direktoriyani yaratish
mkdir -p $BACKUP_DIR

# Database backup
docker compose -f /home/deploy/sew-track/docker-compose.production.yml exec -T db \
    pg_dump -U $DB_USER $DB_NAME | gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz

# Media files backup (agar bor bo'lsa)
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz /home/deploy/sew-track/media/

# Eski backuplarni o'chirish (30 kundan eski)
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
```

**Script'ni executable qilish:**

```bash
chmod +x ~/backup.sh

# Test qilish
./backup.sh
```

**Cron job qo'shish (kunlik backup):**

```bash
crontab -e

# Har kuni soat 3 da:
0 3 * * * /home/deploy/backup.sh >> /home/deploy/backup.log 2>&1
```

---

## 📊 **7-QADAM: Monitoring Sozlash**

### 7.1. Flower (Celery monitoring)

Flower allaqachon ishlamoqda:

```
http://your-domain.com:5555
Login: admin (FLOWER_USER dan)
Password: .env fayldagi FLOWER_PASSWORD
```

**Firewall'da port ochish:**

```bash
sudo ufw allow 5555/tcp
```

### 7.2. Server monitoring (htop)

```bash
# Real-time monitoring
htop

# Disk usage
df -h

# Memory usage
free -h

# Docker stats
docker stats
```

### 7.3. Logs kuzatish

```bash
# Django logs
docker compose -f docker-compose.production.yml logs -f web

# Nginx logs
docker compose -f docker-compose.production.yml logs -f nginx

# Database logs
docker compose -f docker-compose.production.yml logs -f db

# Celery logs
docker compose -f docker-compose.production.yml logs -f celery_worker
```

---

## 🚀 **8-QADAM: Optimizatsiya**

### 8.1. Docker images optimizatsiya

```bash
# Ishlatilmayotgan images va containerlarni tozalash
docker system prune -a --volumes -f
```

### 8.2. PostgreSQL tuning

**Production uchun PostgreSQL sozlamalari:**

Yangi fayl yarating: `postgres-production.conf`

```bash
# Performance tuning
shared_buffers = 512MB
effective_cache_size = 1536MB
work_mem = 8MB
maintenance_work_mem = 128MB
max_connections = 100

# Logging
logging_collector = on
log_directory = 'pg_log'
log_filename = 'postgresql-%Y-%m-%d.log'
log_statement = 'all'
log_duration = on
```

**docker-compose.production.yml da qo'shish:**

```yaml
db:
  volumes:
    - ./postgres-production.conf:/etc/postgresql/postgresql.conf
  command: postgres -c config_file=/etc/postgresql/postgresql.conf
```

### 8.3. Nginx caching

`nginx/conf.d/sewtrack.conf` ga qo'shing:

```nginx
# Cache configuration
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m max_size=1g inactive=60m use_temp_path=off;

# Server blockda:
location / {
    proxy_cache my_cache;
    proxy_cache_valid 200 60m;
    proxy_cache_use_stale error timeout updating http_500 http_502 http_503 http_504;
    # ... other proxy settings
}
```

---

## ✅ **9-QADAM: Production Checklist**

### Pre-launch checklist:

- [ ] **Environment variables:**
  - [ ] SECRET_KEY o'zgartirilgan
  - [ ] DEBUG=False
  - [ ] ALLOWED_HOSTS to'g'ri sozlangan
  - [ ] Database parol mustahkam
  - [ ] SSL enabled (production uchun)

- [ ] **Database:**
  - [ ] Migrations qo'llanilgan
  - [ ] Superuser yaratilgan
  - [ ] Backup sozlangan

- [ ] **Security:**
  - [ ] Firewall yoqilgan
  - [ ] SSL certificate sozlangan
  - [ ] Fail2ban o'rnatilgan
  - [ ] Strong passwords

- [ ] **Docker:**
  - [ ] Barcha containers ishlamoqda
  - [ ] Logs xatolarsiz
  - [ ] Health checks ishlayapti

- [ ] **Domain:**
  - [ ] DNS sozlangan
  - [ ] SSL certificate active
  - [ ] HTTP → HTTPS redirect ishlayapti

- [ ] **Monitoring:**
  - [ ] Flower accessible
  - [ ] Logs configured
  - [ ] Backup tested

- [ ] **Testing:**
  - [ ] Login ishlayapti
  - [ ] Work records create/view
  - [ ] Static files serve bo'lyapti
  - [ ] Media uploads ishlayapti
  - [ ] Celery tasks ishlayapti

---

## 🔄 **10-QADAM: Deployment Updates**

### Yangi versiyani deploy qilish:

```bash
cd ~/sew-track

# 1. Git pull
git pull origin main

# 2. Rebuild containers (agar kod o'zgargan bo'lsa)
docker compose -f docker-compose.production.yml build

# 3. Stop services
docker compose -f docker-compose.production.yml down

# 4. Start with new code
docker compose -f docker-compose.production.yml up -d

# 5. Run migrations (agar bor bo'lsa)
docker compose -f docker-compose.production.yml exec web python manage.py migrate

# 6. Collect static files (agar frontend o'zgargan bo'lsa)
docker compose -f docker-compose.production.yml exec web python manage.py collectstatic --noinput

# 7. Check logs
docker compose -f docker-compose.production.yml logs -f
```

### Zero-downtime deployment (Advanced):

```bash
# Blue-green deployment uchun:
# 1. Yangi containers yaratish (boshqa port)
# 2. Health check
# 3. Nginx proxy_pass ni yangi portga o'zgartirish
# 4. Eski containerlarni to'xtatish
```

---

## 🆘 **Troubleshooting**

### Muammo: Containers ishlamayapti

```bash
# Logs tekshiring
docker compose -f docker-compose.production.yml logs

# Container holatini tekshiring
docker compose -f docker-compose.production.yml ps

# Restart qiling
docker compose -f docker-compose.production.yml restart
```

### Muammo: Database connection error

```bash
# Database container ishlayaptimi?
docker compose -f docker-compose.production.yml ps db

# Database logs
docker compose -f docker-compose.production.yml logs db

# .env fayldagi DB credentials to'g'rimi?
cat .env | grep DB_
```

### Muammo: Static files 404

```bash
# Collectstatic qayta ishga tushiring
docker compose -f docker-compose.production.yml exec web python manage.py collectstatic --noinput

# Nginx configuration tekshiring
docker compose -f docker-compose.production.yml exec nginx nginx -t

# Nginx restart
docker compose -f docker-compose.production.yml restart nginx
```

### Muammo: SSL certificate xatosi

```bash
# Certificate files bormi?
ls -la ~/sew-track/nginx/ssl/

# Certbot renew
sudo certbot renew --dry-run

# Nginx restart
docker compose -f docker-compose.production.yml restart nginx
```

### Muammo: High memory usage

```bash
# Memory monitoring
free -h
docker stats

# Eski logs tozalash
docker compose -f docker-compose.production.yml exec web sh -c "find /app/logs -name '*.log' -mtime +7 -delete"

# Restart services
docker compose -f docker-compose.production.yml restart
```

---

## 📱 **11-QADAM: Post-Deployment**

### 11.1. Foydalanuvchilarga yo'riqnoma

Workers uchun:
```
Website: https://your-domain.com
Login: Username (bergan usernamelar)
Password: Boshlang'ich parol (keyinchalik o'zgartirish kerak)
```

### 11.2. Admin panel sozlash

```
Admin: https://your-domain.com/admin/
Superuser: Sizning yaratganingiz
```

### 11.3. TV Dashboard

```
TV Display: https://your-domain.com/dashboard/tv/
Auto-refresh: Ha (30s interval)
Fullscreen: Brauzerda F11
```

---

## 🎉 **Tabriklaymiz!**

SEW-TRACK tizimi production serverda ishga tushirildi! 🚀

### **Keyingi qadamlar:**

1. ✅ Workers'ni train qiling
2. ✅ Real ma'lumotlarni kiriting
3. ✅ Feedback yig'ing
4. ✅ Monitor qiling
5. ✅ Optimize qiling

---

## 📞 **Yordam kerakmi?**

### **Umumiy muammolar:**
- Logs tekshiring
- Documentation qayta o'qing
- StackOverflow search qiling

### **Production support:**
- Server monitoring: htop, docker stats
- Logs: docker compose logs
- Backup: Kunlik automatic

---

## 📚 **Qo'shimcha resurslar:**

- **Django docs:** https://docs.djangoproject.com/
- **Docker docs:** https://docs.docker.com/
- **Nginx docs:** https://nginx.org/en/docs/
- **Let's Encrypt:** https://letsencrypt.org/
- **DigitalOcean tutorials:** https://www.digitalocean.com/community/tutorials

---

**Created with ❤️ for Uzbekistan's textile industry**

**Status:** Production-Ready ✅  
**Last Updated:** November 11, 2024  
**Version:** 1.0.0

