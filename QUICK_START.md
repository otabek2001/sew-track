# 🚀 SEW-TRACK - Quick Start Guide

## 📋 Loyiha haqida

**SEW-TRACK** - Tikuvchilik tsexlari uchun ishlab chiqilgan ishchilar faoliyatini kuzatish va maosh hisoblash tizimi.

## ✅ Hozirgi holat (Phase 2 - Tugallandi)

### Yaratilgan App'lar:

1. **Accounts** ✅
   - Custom User model (email authentication)
   - JWT authentication (login/refresh)
   - User roles: super_admin, tenant_admin, master, worker, accountant, viewer
   - Password management

2. **Employees** ✅
   - Employee profiles
   - User bilan bog'lanish
   - Position: worker, master, quality_controller, supervisor
   - Employment type: full_time, part_time, contract, temporary

3. **Tasks** ✅
   - Operations (tikuv operatsiyalari)
   - Categories: cutting, sewing, ironing, packaging, quality_check
   - O'zbek va rus tillarida nomlar

4. **Products** ✅
   - Mahsulot katalogi
   - Article codes (ART-001, ART-002...)
   - ProductTask - mahsulot va operatsiya bog'lanishi
   - Base va premium narxlar

### Database:
- ✅ PostgreSQL 16 (Docker)
- ✅ Redis 7 (Docker)
- ✅ Barcha migration'lar bajarilgan
- ✅ Test data yuklangan

## 🚀 Ishga tushirish

### 1. Virtual Environment
```bash
source venv/bin/activate
```

### 2. Docker Services
```bash
# PostgreSQL va Redis'ni ishga tushirish
docker-compose up -d db redis

# Statusni tekshirish
docker-compose ps
```

### 3. Database Migration
```bash
python manage.py migrate
```

### 4. Test Data
```bash
# Test data yaratish (Tasks, Products)
python scripts/init_test_data.py
```

### 5. Development Server
```bash
python manage.py runserver
```

## 🌐 Endpoints

### Main
- **Home**: http://localhost:8000
- **Admin**: http://localhost:8000/admin
- **API Docs**: http://localhost:8000/api/docs/
- **API Schema**: http://localhost:8000/api/schema/

### API v1

#### Authentication
- `POST /api/v1/accounts/auth/login/` - Login
- `POST /api/v1/accounts/auth/refresh/` - Refresh token

#### Users
- `GET /api/v1/accounts/users/` - List users
- `POST /api/v1/accounts/users/` - Create user
- `GET /api/v1/accounts/users/me/` - Current user
- `POST /api/v1/accounts/users/change_password/` - Change password

#### Employees
- `GET /api/v1/employees/` - List employees
- `POST /api/v1/employees/` - Create employee
- `GET /api/v1/employees/{id}/` - Employee details
- `GET /api/v1/employees/me/` - Current employee profile
- `POST /api/v1/employees/{id}/activate/` - Activate
- `POST /api/v1/employees/{id}/deactivate/` - Deactivate

#### Products
- `GET /api/v1/products/` - List products
- `POST /api/v1/products/` - Create product
- `GET /api/v1/products/{id}/` - Product details
- `GET /api/v1/products/{id}/tasks/` - Product tasks
- `POST /api/v1/products/{id}/add_task/` - Add task to product

#### Tasks
- `GET /api/v1/tasks/` - List tasks
- `POST /api/v1/tasks/` - Create task
- `GET /api/v1/tasks/{id}/` - Task details
- `GET /api/v1/tasks/categories/` - Task categories
- `GET /api/v1/tasks/active/` - Active tasks

## 🧪 Test Data

### Ma'lumotlar:

**Tasks:**
- TASK-001: Олди релф лента ёпиштириш (450 UZS)
- TASK-002: Орқа релф лента ёпиштириш (450 UZS)
- TASK-003: Елка тикиш (800 UZS)
- TASK-004: Пиджак тикиш
- TASK-005: Даўлаш (200 UZS)

**Products:**
- ART-034: Женский костюм (юбка)
- ART-035: Женский костюм (пиджак)
- ART-036: Мужской костюм

## 📱 Test API

### 1. Login
```bash
curl -X POST http://localhost:8000/api/v1/accounts/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@sewtrack.uz",
    "password": "admin123"
  }'
```

### 2. Get Tasks
```bash
curl -X GET http://localhost:8000/api/v1/tasks/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. Get Products
```bash
curl -X GET http://localhost:8000/api/v1/products/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🛠️ Development Commands

### Code Quality
```bash
# Linting
ruff check .

# Type checking
mypy .

# Format code
ruff format .
```

### Testing
```bash
# Run tests
pytest

# With coverage
pytest --cov
```

### Database
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### Celery (background tasks)
```bash
# Worker
celery -A celery_app worker -l info

# Beat (scheduler)
celery -A celery_app beat -l info

# Flower (monitoring)
celery -A celery_app flower
```

## 📊 Database Schema

### Current Models:
- ✅ **User** - Authentication va role management
- ✅ **Employee** - Xodim ma'lumotlari
- ✅ **Task** - Operatsiyalar
- ✅ **Product** - Mahsulotlar
- ✅ **ProductTask** - Mahsulot-operatsiya bog'lanish

### Next Phase (Phase 3):
- ⏳ **WorkRecord** - Ish yozuvlari
- ⏳ **MasterRecord** - Master yozuvlari
- ⏳ **Reconciliation** - Ma'lumotlar sverkasi
- ⏳ **WagePeriod** - Maosh davri
- ⏳ **WageCalculation** - Maosh hisoblash

## 🔧 Texnologiyalar

- **Backend**: Django 5.2.8 + DRF 3.15.2
- **Database**: PostgreSQL 16
- **Cache**: Redis 7
- **Tasks**: Celery 5.4.0
- **Auth**: JWT (djangorestframework-simplejwt)
- **Docs**: drf-spectacular
- **Python**: 3.14.0

## 📁 Struktura

```
sew-track/
├── apps/                      # Django applications
│   ├── accounts/             # Users & Auth
│   ├── employees/            # Employee management
│   ├── products/             # Products catalog
│   └── tasks/                # Operations
├── core/                      # Shared utilities
├── config/                    # Django settings
│   └── settings/             # Environment-based settings
├── celery_app/               # Celery configuration
├── requirements/             # Dependencies
├── scripts/                  # Helper scripts
├── templates/                # HTML templates
├── static/                   # Static files
├── media/                    # Uploaded files
└── tests/                    # Tests

```

## 📝 Notes

- Server running: http://localhost:8000
- Database: PostgreSQL on localhost:5432
- Redis: localhost:6381 (mapped from 6379)

---

**Status**: ✅ Phase 2 Completed
**Next**: Phase 3 - Work Records & Reconciliation

