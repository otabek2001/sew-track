# 🧵 SEW-TRACK: Tikuv sexi boshqaruv platformasi

[![Django](https://img.shields.io/badge/Django-5.2-green.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.15-red.svg)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

> Konveyer usulida ishlaydigan tikuv sexlari uchun professional ish hisobi va ish haqi hisoblash tizimi

[🇺🇿 O'zbekcha](docs/SUMMARY_UZ.md) | [🇷🇺 Русский](docs/SUMMARY_RU.md) | [📖 Full Concept](docs/PROJECT_CONCEPT.md)

---

## 📋 Loyiha haqida

**SEW-TRACK** - bu tikuv sexlari uchun ishlab chiqilgan zamonaviy veb-platforma bo'lib, quyidagilarni avtomatlashtiradi:

- ✅ Ishchilarning bajargan ishlarini ro'yxatga olish
- ✅ Master tomonidan nazorat va tasdiqlash
- ✅ Ma'lumotlarni avtomatik solishtirish va xatoliklarni aniqlash
- ✅ Ish haqini avtomatik hisoblash (sifat bonuslari va jarimalar bilan)
- ✅ Kunlik, oylik va umumiy hisobotlar

## 🎯 Asosiy xususiyatlar

### 🔄 Konveyer ishi
15-20 kishilik jamoada har bir ishchi o'z operatsiyasini bajaradi (yoqa tikish, tugma qadash, press qilish va h.k.). Tizim har bir ishchining ishini alohida hisobga oladi.

### 📊 Ikki tomonlama nazorat
- **Ishchi**: O'zi bajargan ishini kunlik kiritadi
- **Master**: Umumiy natijani smenaning oxirida kiritadi
- **Tizim**: Avtomatik solishtiradi va farqlarni ko'rsatadi

### 💰 Adolatli ish haqi
- Faqat tasdiqlangan ishlarga to'lanadi
- Sifat bonuslari (95%+ aniqlik uchun 10% bonus)
- Katta farqlar uchun jarimalar
- Shaffof hisob-kitob

## 🏗️ Texnologiyalar

```
Backend:      Django 5.2 + Django REST Framework 3.15
Database:     PostgreSQL 16
Cache:        Redis 7
Task Queue:   Celery 5
API Docs:     OpenAPI 3.0 (drf-spectacular)
Auth:         JWT (djangorestframework-simplejwt)
Deploy:       Docker + Docker Compose
```

## 📁 Loyiha strukturasi

```
sew-track/
├── apps/                   # Django ilovalar
│   ├── accounts/          # Foydalanuvchilar
│   ├── employees/         # Xodimlar
│   ├── products/          # Mahsulotlar
│   ├── tasks/             # Operatsiyalar
│   ├── work_records/      # Ish yozuvlari
│   ├── reconciliation/    # Solishtirish
│   └── wages/             # Ish haqi
├── core/                  # Umumiy utilities
├── config/                # Django sozlamalar
├── docs/                  # Hujjatlar
└── requirements/          # Dependencies
```

## 🚀 Ishga tushirish

### Talablar

- Python 3.11+
- PostgreSQL 16+
- Redis 7+
- Docker & Docker Compose (ixtiyoriy)

### Docker bilan

```bash
# Repository ni clone qiling
git clone https://github.com/yourusername/sew-track.git
cd sew-track

# .env faylini yarating
cp .env.example .env
# .env faylini o'z sozlamalaringiz bilan to'ldiring

# Docker container larni ishga tushiring
docker-compose up -d

# Migratsiyalarni bajaing
docker-compose exec web python manage.py migrate

# Superuser yarating
docker-compose exec web python manage.py createsuperuser

# Dastlabki ma'lumotlarni yuklang (tasks ro'yxati)
docker-compose exec web python manage.py load_tasks
```

Tizim `http://localhost:8000` da ochiladi

### Manual o'rnatish

```bash
# Virtual environment yarating
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Dependencies ni o'rnating
pip install -r requirements/development.txt

# .env faylini sozlang
cp .env.example .env

# Migratsiyalarni bajaring
python manage.py migrate

# Serverni ishga tushiring
python manage.py runserver
```

## 📚 Hujjatlar

- **[PROJECT_CONCEPT.md](docs/PROJECT_CONCEPT.md)** - To'liq loyiha kontseptsiyasi (rus tilida)
- **[SUMMARY_UZ.md](docs/SUMMARY_UZ.md)** - Qisqacha tavsif (o'zbek tilida)
- **[SUMMARY_RU.md](docs/SUMMARY_RU.md)** - Краткое описание (rus tilida)

## 🔑 API Endpointlar

### Autentifikatsiya
```
POST   /api/v1/auth/login/           # Login
POST   /api/v1/auth/refresh/         # Token yangilash
GET    /api/v1/auth/me/              # Joriy foydalanuvchi
```

### Ish yozuvlari
```
GET    /api/v1/work-records/                  # Ro'yxat
POST   /api/v1/work-records/                  # Yaratish
GET    /api/v1/work-records/my-records/       # Mening yozuvlarim
GET    /api/v1/work-records/daily-summary/    # Kunlik hisobot
```

### Ish haqi
```
GET    /api/v1/wages/periods/                 # Davrlar ro'yxati
POST   /api/v1/wages/calculations/calculate/  # Hisoblash
GET    /api/v1/wages/calculations/{id}/       # Hisob natijasi
```

**API dokumentatsiya**: `http://localhost:8000/api/docs/`

## 🧪 Testlar

```bash
# Barcha testlarni ishga tushirish
pytest

# Coverage bilan
pytest --cov=apps --cov-report=html

# Bitta app ni test qilish
pytest apps/work_records/tests.py
```

## 👥 Foydalanuvchi rollari

| Rol | Huquqlar |
|-----|----------|
| **Admin** | To'liq kirish, sozlamalar |
| **Master** | Ish kiritish, solishtirish, barcha hisobotlar |
| **Worker** | O'z ishini kiritish, o'z hisobotlari |
| **Accountant** | Ish haqini hisoblash, moliyaviy hisobotlar |

## 🛣️ Rivojlanish yo'l xaritasi

- [x] Loyiha kontseptsiyasi
- [x] Ma'lumotlar bazasi dizayni
- [ ] Phase 1: Asosiy struktura (1 hafta)
- [ ] Phase 2: Bazaviy ilovalar (1-2 hafta)
- [ ] Phase 3: Ish hisobi (2 hafta)
- [ ] Phase 4: Solishtirish (1-2 hafta)
- [ ] Phase 5: Ish haqi (1-2 hafta)
- [ ] Phase 6: UI va hisobotlar (2 hafta)
- [ ] Phase 7: Test va deploy (1 hafta)

## 🤝 Hissa qo'shish

Hissa qo'shmoqchi bo'lsangiz:

1. Repository ni fork qiling
2. Feature branch yarating (`git checkout -b feature/AmazingFeature`)
3. O'zgarishlarni commit qiling (`git commit -m 'Add some AmazingFeature'`)
4. Branch ga push qiling (`git push origin feature/AmazingFeature`)
5. Pull Request oching

## 📞 Aloqa

**Muallif**: Professional Fullstack Developer  
**Email**: [your.email@example.com](mailto:your.email@example.com)  
**Telegram**: [@yourusername](https://t.me/yourusername)

## 📄 Litsenziya

Ushbu loyiha MIT litsenziyasi ostida tarqatiladi. Tafsilotlar uchun [LICENSE](LICENSE) faylini ko'ring.

## 🙏 Minnatdorchilik

- Django va DRF jamiyatiga
- PostgreSQL jamoasiga
- Barcha open-source hissa qo'shuvchilarga

---

**Made with ❤️ for Uzbekistan's textile industry**

