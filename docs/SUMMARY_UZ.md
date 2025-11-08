# SEW-TRACK: Loyiha qisqacha tavsifi

## 🎯 Bu nima?

**SEW-TRACK** - konveyer usulida ishlaydigan 15-20 kishilik tikuv sexi uchun boshqaruv veb-platformasi.

## ⚙️ Asosiy funksiyalar

### 1. **Ishlar hisobi**
- Ishchi bajargan ishlarni ro'yxatga oladi (necha dona qilgani)
- Master smenaning umumiy natijalarini ro'yxatga oladi
- Tizim avtomatik ravishda ma'lumotlarni solishtiradi

### 2. **Mahsulotlar va operatsiyalar**
- Mahsulotlar bazasi (masalan: ART-034 - ayollar kostyumi)
- Har bir mahsulot uchun narxlari bilan operatsiyalar ro'yxati
- Misol: "Олди релф лента ёпиштириш" - 450 so'm

### 3. **Ma'lumotlarni solishtiish**
- Ishchi va master ma'lumotlarini avtomatik solishtirish
- Farqlarni aniqlash
- Katta farqlar haqida xabarnomalar

### 4. **Ish haqi hisobi**
- Hisob-kitob davrlari (oy, davr)
- Tasdiqlangan ishlarga ko'ra avtomatik hisoblash
- Sifat bonuslari (master bilan aniq mos kelish)
- Farqlar uchun jarimalar

### 5. **Hisobotlar**
- Ishchining kunlik hisoboti
- Oylik hisobot va statistika
- Master hisobotlari
- Sex analitikasi

## 🏗️ Texnologiyalar

- **Backend**: Django 5.2 + Django REST Framework
- **Ma'lumotlar bazasi**: PostgreSQL 16
- **Kesh/Navbat**: Redis + Celery
- **API**: JWT autentifikatsiya bilan REST API
- **Hujjatlar**: OpenAPI 3.0 (Swagger)
- **Deploy**: Docker + Docker Compose

## 📊 Ma'lumotlar bazasi

### Asosiy modellar:

1. **User** - tizim foydalanuvchilari
2. **Employee** - sex xodimlari
3. **Product** - mahsulotlar (artikullar)
4. **Task** - operatsiyalar/vazifalar
5. **ProductTask** - mahsulotlarga operatsiyalarni narxlar bilan bog'lash
6. **WorkRecord** - ish yozuvlari (ishchi va master)
7. **Reconciliation** - solishtirish natijalari
8. **WagePeriod** - ish haqi hisoblash davrlari
9. **WageCalculation** - ish haqi hisoblari

## 🔐 Foydalanuvchi rollari

- **Admin** - to'liq kirish
- **Master** - ma'lumotlarni kiritish, solishtirish, barcha hisobotlarni ko'rish
- **Worker** - o'z ma'lumotlarini kiritish, o'z hisobotlarini ko'rish
- **Accountant** - ish haqini hisoblash, moliyaviy hisobotlar

## 🚀 Ish jarayoni

### Har kuni:

1. **Ertalab**: Ishchilar smenani boshlaydi
2. **Kun davomida**: Ishchilar bajargan operatsiyalarni tizim orqali ro'yxatga oladi
3. **Kechqurun**: Master smenaning yakuniy ma'lumotlarini kiritadi
4. **Kechasi (00:00)**: Celery orqali avtomatik solishtirish

### Oy oxirida:

1. Admin/buxgalter hisob-kitob davrini yaratadi
2. Tizim hammaning ish haqini avtomatik hisoblab chiqadi
3. Bonuslar va jarimalar qo'llaniladi
4. To'lov uchun hisobotlar shakllantiriladi

## 📱 API Misollari

### Ishni ro'yxatga olish:
```http
POST /api/v1/work-records/
{
  "product_id": "uuid",
  "task_id": "uuid",
  "quantity": 15,
  "work_date": "2024-11-08"
}
```

### Kunlik hisobot:
```http
GET /api/v1/work-records/daily-summary/?date=2024-11-08
```

### Ish haqini hisoblash:
```http
POST /api/v1/wages/calculations/calculate/
{
  "period_id": "uuid",
  "employee_ids": ["uuid1", "uuid2"]
}
```

## 📈 Afzalliklar

✅ **Avtomatlashtirish** - qo'l ishi minimal
✅ **Shaffoflik** - har kim o'z progressini ko'radi
✅ **Sifat nazorati** - avtomatik solishtirish
✅ **Adolatlilik** - aniq ish haqi hisobi
✅ **Analitika** - samaradorlikni tushunish

## ⏱️ Ishlab chiqish muddatlari

- **MVP (asosiy funksional)**: 4-5 hafta
- **To'liq versiya**: 8-10 hafta
- **Qo'llab-quvvatlash**: doimiy

## 💡 Keyingi qadamlar

1. ✅ Kontseptsiyani tasdiqlash
2. Talablarni detallash
3. Ishlab chiqishni boshlash
4. Pilot guruhda test qilish
5. Joriy etish

---

**Savollar?** Barcha tafsilotlar `PROJECT_CONCEPT.md` da

