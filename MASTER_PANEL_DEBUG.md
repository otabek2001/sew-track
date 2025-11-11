# 🔧 Master Panel Debug Guide

## ❓ Muammo: "Faqat 'Rad etish' ko'rinayapti"

Keling, qadamma-qadam tekshiramiz:

---

## ✅ **Avval tekshirish kerak:**

### **1. Login to'g'ri amalga oshyaptimi?**
```
URL: http://localhost:8000/login/
Username: rustam
Password: Password123!
```

**Kutilayotgan:**
- ✅ Auto-redirect to: `/master/` (master dashboard)
- ❌ Agar `/dashboard/` ga redirect bo'lsa - permission muammosi!

---

### **2. Test sahifani ochib ko'ring:**
```
http://localhost:8000/master/test/
```

**Bu sahifada:**
- ✅ 2 ta test card
- ✅ Har birida "Tasdiqlash" va "Rad etish" tugmalari
- ✅ Alpine.js test (modal)

**Agar test sahifada tugmalar ko'rinsa:**
- CSS/Tailwind ishlayapti ✅
- Alpine.js ishlayapti ✅
- Muammo real sahifada

**Agar test sahifada ham ko'rinmasa:**
- CSS yuklanmagan ❌
- Brauzer cache muammosi

---

### **3. Master Dashboard ochib ko'ring:**
```
http://localhost:8000/master/
```

**Ko'rinishi kerak:**
- 🔔 Alert: "87 ta yozuv kutmoqda"
- 📊 2 ta stat card
- 🎯 4 ta quick action button
- 📝 So'nggi faollik

**Agar ko'rinmasa:**
- Permission muammosi (redirect to /dashboard/)
- Template yo'q

---

### **4. Pending list ochib ko'ring:**
```
http://localhost:8000/master/pending/
```

**Ko'rinishi kerak:**
- Filters (Date/Employee/Product)
- Statistics (87 ta yozuv)
- List of pending records

**Har bir record da:**
- ☐ Checkbox (chap tomonda)
- 👤 Employee name
- 📦 Product name
- ⚙️ Task name
- 📊 Quantity + Payment
- 📅 Date
- **✅ Tasdiqlash** (yashil tugma) ← BU BOR BO'LISHI KERAK!
- **❌ Rad etish** (qizil tugma)

---

## 🐛 **Muammoni Topish:**

### **Browser Console (F12) tekshiring:**

1. **Elements tab:**
   - Pending approvals sahifani oching
   - Bitta record topib, inspect qiling
   - "Tasdiqlash" button HTML da bormi?
   - CSS styles nima?

2. **Console tab:**
   - Xatoliklar bormi?
   - Alpine.js yuklanganni?
   - `Alpine is not defined` xatosi?

3. **Network tab:**
   - Page load qilganda barcha resources yuklanyaptimi?
   - Tailwind CSS (cdn.tailwindcss.com)
   - Alpine.js (cdn.jsdelivr.net)

---

## 🔍 **Ehtimoliy Muammolar:**

### **Muammo 1: Alpine.js yuklanmagan**
**Alomat:** Modal ishlamaydi, x-data ishlam aydi

**Yechim:**
```html
<!-- base.html da bormi? -->
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.13.5/dist/cdn.min.js"></script>
```

---

### **Muammo 2: CSS yuklanmagan**
**Alomat:** Tugmalar oddiy HTML ko'rinishida

**Yechim:**
- Hard refresh: Ctrl+Shift+R
- Clear cache
- Incognito mode

---

### **Muammo 3: Template xatosi**
**Alomat:** Tugma HTML da yo'q

**Yechim:**
Pending approvals templateda quyidagi kod bormi:

```html
<button class="...bg-green-600...">
    <i data-lucide="check"></i>
    Tasdiqlash
</button>
```

---

### **Muammo 4: Permission muammosi**
**Alomat:** `/master/pending/` ochilmaydi, redirect bo'ladi

**Yechim:**
Rustam user to'g'ri sozlanganmi?
```bash
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
rustam = User.objects.get(username='rustam')
print(f'Role: {rustam.role}')
print(f'Is Staff: {rustam.is_staff}')
print(f'Is Master: {rustam.is_master_or_above}')
"
```

---

## 💡 **ODDIY TEST:**

### **1. Test page (simplified):**
```
http://localhost:8000/master/test/
```

Agar bu sahifada 2 ta tugma (Tasdiqlash va Rad etish) ko'rinsa:
- ✅ CSS ishlayapti
- ✅ Alpine.js ishlayapti
- ❌ Muammo real sahifa templateda

Agar ko'rinmasa:
- ❌ CSS yuklanmagan
- ❌ Browser cache
- ❌ Internet connection (CDN resources)

---

### **2. Browser DevTools:**

**F12 bosing:**

**Console tab:**
```javascript
// Type va enter bosing:
typeof Alpine
// Natija: "object" bo'lishi kerak

typeof tailwind  
// Natija: "object" bo'lishi kerak

document.querySelector('.bg-green-600')
// Natija: button element yoki null
```

**Elements tab:**
```html
<!-- Search for: bg-green-600 -->
<!-- "Tasdiqlash" button topilishi kerak -->
```

---

## 🔧 **Quick Fix Commands:**

### **Fix 1: Hard Refresh**
```
Ctrl + Shift + R (Windows/Linux)
Cmd + Shift + R (Mac)
```

### **Fix 2: Clear Cache**
```
F12 → Network tab → "Disable cache" checkbox
F5 refresh
```

### **Fix 3: Incognito Mode**
```
Ctrl + Shift + N (Chrome)
Test in clean environment
```

---

## 📸 **Screenshot kerak:**

Agar muammo davom etsa:

1. Browser screenshot oling:
   - Full page view
   - One pending record (zoomed)
   - Browser console errors

2. Share qiling yoki describe qiling:
   - Nima ko'rinyapti?
   - Qaysi tugma yo'q?
   - Console da xatolik bormi?

---

## 🎯 **Expected View:**

### **Har bir pending record:**
```
┌────────────────────────────────────┐
│ ☐  👤 Shahnoza Karimova           │
│    Ayollar ko'ylagi               │
│    Tikish                         │
│    10 dona • 50,000 so'm          │
│    📅 10.11.2025 • 2 soat oldin   │
│                                    │
│  [✅ Tasdiqlash] [❌ Rad etish]    │
│   (yashil)         (qizil)        │
└────────────────────────────────────┘
```

---

## ✅ **Test URLs:**

```
1. Test page:      http://localhost:8000/master/test/
2. Master dashboard: http://localhost:8000/master/
3. Pending list:   http://localhost:8000/master/pending/
```

**Qaysi sahifada muammo bor?** 

- All pages?
- Only pending list?
- Specific records?

---

**Brauzerda test qiling va natijani aytib bering:**
1. Test page (`/master/test/`) - buttons ko'rinyaptimi?
2. Pending list (`/master/pending/`) - nima ko'rinyapti?
3. Browser console - xatoliklar bormi?

📱🔧

