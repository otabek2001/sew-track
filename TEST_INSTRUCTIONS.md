# 🧪 Test Instructions - Work Records

## ✅ HTMX Loop Fix Applied!

Cheksiz request muammosi hal qilindi! 

**Nima o'zgartirildi:**
- ❌ HTMX `hx-trigger="load from:body"` olib tashlandi
- ✅ Alpine.js fetch API ishlatildi
- ✅ Manual DOM update
- ✅ No more infinite loops!

---

## 🚀 Test Qilish (Qadamma-qadam)

### 1️⃣ **Brauzerda login qiling:**

```
URL: http://localhost:8000/login/
Username: shahnoza
Password: Password123!
```

### 2️⃣ **Dashboard ochiladi:**
```
http://localhost:8000/dashboard/
```

Dashboard da:
- ✅ "Yangi yozuv" tugmasi
- ✅ "Yozuvlarim" tugmasi  
- ✅ Bottom navigation
- ✅ Quick actions cards

### 3️⃣ **"Yangi yozuv" tugmasini bosing:**

Yoki to'g'ridan-to'g'ri URL:
```
http://localhost:8000/api/v1/tasks/work-records/create/
```

### 4️⃣ **Form elementlarini tekshiring:**

**Step 1: Mahsulot tanlash**
- Dropdown ochish
- 3 ta mahsulot ko'rinishi kerak:
  - ART-001 - Ayollar ko'ylagi
  - ART-002 - Erkaklar ko'ylagi
  - ART-003 - Bolalar ko'ylagi

**Step 2: Operatsiya tanlash** (Auto-loads)
- Mahsulot tanlagandan keyin avtomatik yuklanadi
- Loading state ko'rinadi
- Operatsiyalar dropdown da paydo bo'ladi
- Console da "Tasks loaded: [...]" ko'rinadi

**Step 3: Miqdor kiritish**
- Number input
- Minimum: 1
- Real-time price calculation

**Step 4: Narx ko'rsatish**
- Gradient card
- Birlik narxi
- Jami to'lov
- Uzbek format (1,000 so'm)

**Step 5: Saqlash**
- "Saqlash" tugmasi
- Redirect work records list ga

---

## 🐛 Debugging

### Browser Console (F12) da ko'rinishi kerak:

```
✅ Lucide icons initialized
✅ Icons initialized
Libraries status:
- Tailwind: ✅
- Alpine: ✅
- HTMX: ✅
- Lucide: ✅

Product changed: <uuid>
Tasks loaded: [{id: "...", name: "..."}]
Price calculated: {per_unit: "5,000", total: "50,000"}
```

### Network Tab da:
- ✅ `/api/product/<id>/tasks/` - 1 marta (product tanlanganda)
- ✅ `/api/calculate-price/` - 1 marta (quantity kiritganda)
- ❌ Cheksiz requestlar YO'Q bo'lishi kerak!

---

## 📝 Test Scenario:

1. **Login:** shahnoza / Password123!
2. **Dashboard:** "Yangi yozuv" → Click
3. **Product:** ART-001 (Ayollar ko'ylagi) → Select
4. **Wait:** Tasks load automatically
5. **Task:** TASK-001 (Tikish - 5,000 so'm) → Select
6. **Quantity:** 10 → Type
7. **See:** Jami to'lov: 50,000 so'm
8. **Submit:** "Saqlash" → Click
9. **Redirect:** Work records list page
10. **Verify:** New record shows in list

---

## ✅ Expected Behavior:

### Product change:
```
1. Select product
2. Tasks dropdown shows "Yuklanmoqda..."
3. Fetch /api/product/{id}/tasks/
4. Tasks dropdown populated
5. Price resets to 0
```

### Task + Quantity change:
```
1. Select task
2. Enter quantity
3. Fetch /api/calculate-price/
4. Gradient card shows with price
5. No infinite requests!
```

---

## 🔧 If Still Not Working:

### Check Console Errors:
```javascript
// Should NOT see:
❌ HTMX infinite loop
❌ Failed to fetch
❌ Uncaught errors

// Should see:
✅ Product changed
✅ Tasks loaded
✅ Price calculated
```

### Check Network:
```
Should see:
- 1x GET /api/v1/tasks/work-records/create/ (HTML)
- 1x GET /api/product/{id}/tasks/ (when product selected)
- 1x GET /api/calculate-price/ (when quantity entered)

Should NOT see:
- Repeated requests
- Failed requests (red in Network tab)
```

---

## 📱 Mobile Test:

1. Open in mobile browser (or Chrome DevTools mobile mode)
2. All inputs should be 44px+ height
3. Touch targets responsive
4. Dropdown easy to select
5. Number input easy to type

---

## 🎯 Success Criteria:

- [ ] Page loads WITHOUT infinite loop
- [ ] Product dropdown works
- [ ] Task dropdown loads dynamically
- [ ] Quantity input works
- [ ] Price calculates in real-time
- [ ] Submit button enabled when all filled
- [ ] Form submits successfully
- [ ] Redirect to list page
- [ ] New record appears in list

---

## 🚀 Test Now:

**Open in browser:**
```
http://localhost:8000/login/
```

**Login and test the form!** 📱

Natijani aytib bering! ✨

