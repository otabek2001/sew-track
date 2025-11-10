# 🔧 Troubleshooting - Network Connection Issues

## ❌ Muammo: Telefonda ochilmayapti

Server localhost da ishlayapti ✅  
Lekin 192.168.0.113:8000 da ishlamayapti ❌

---

## 🔍 Diagnostika

### ✅ Server holati:
```
Port: 8000
Interface: 0.0.0.0 (barcha interfacelar)
Status: LISTEN ✅
```

### ❌ Muammo:
MacOS Firewall yoki network sozlamalari tufayli tashqi ulanishlar bloklangan.

---

## 💡 Yechimlar

### Yechim 1: MacOS Firewall sozlamalari (TAVSIYA ETILADI)

#### A. System Preferences orqali:
1. **System Preferences** > **Security & Privacy** > **Firewall**
2. Agar Firewall yoniq bo'lsa:
   - **Firewall Options** ni bosing
   - **+** tugmasini bosing  
   - Python yoki Terminal ni qo'shing
   - **Allow incoming connections** ni belgilang
   - **OK** ni bosing

#### B. Terminal orqali (sudo kerak):
```bash
# Firewall ni vaqtincha o'chirish (test uchun)
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate off

# Test qiling, keyin qayta yoqing:
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate on
```

---

### Yechim 2: ngrok orqali (OSON, FIREWALL MUAMMOSIZ)

Bu eng oson yechim - internet orqali tunnel yaratadi:

```bash
# 1. ngrok o'rnating
brew install ngrok

# 2. ngrok ishga tushiring
ngrok http 8000

# 3. Ko'rsatilgan URL dan foydalaning
# Masalan: https://abc123.ngrok.io
```

**Afzalliklari:**
- ✅ Firewall muammosi yo'q
- ✅ Istalgan joydan kirish mumkin
- ✅ HTTPS bilan
- ✅ Oson sozlash

---

### Yechim 3: Localhost dan test qilish

Agar telefonda test qilish shart bo'lmasa:

```bash
# Kompyuterda brauzer oching:
http://localhost:8000/login/

# Chrome Developer Tools:
F12 > Toggle device toolbar (Ctrl+Shift+M)
# iPhone/Android preview
```

---

### Yechim 4: Portni o'zgartirish

Ba'zan 8000 port firewall da bloklangan:

```bash
# 8080 portda ishga tushiring
python manage.py runserver 0.0.0.0:8080

# Telefonda:
http://192.168.0.113:8080/login/
```

---

### Yechim 5: Wi-Fi Router sozlamalari

Ba'zi routerlar AP Isolation (Client Isolation) yoqilgan bo'ladi:

1. Router admin paneliga kiring (odatda 192.168.0.1 yoki 192.168.1.1)
2. **Wireless Settings** > **AP Isolation**
3. AP Isolation ni **Disable** qiling
4. Router ni restart qiling

---

## 🚀 Quick Test: ngrok bilan (ENG OSON)

```bash
# 1. Terminal 1: Django server
cd /Users/otabeksayfullayev/PycharmProjects/sew-track
source venv/bin/activate
python manage.py runserver

# 2. Terminal 2: ngrok
ngrok http 8000
```

**ngrok natijasi:**
```
Forwarding   https://abc123.ngrok.io -> http://localhost:8000
```

**Telefonda ochish:**
```
https://abc123.ngrok.io/login/
```

---

## ✅ Tavsiya qilinadigan yechim

### Development uchun: ngrok
- Oson, tez, xavfsiz
- Firewall muammosi yo'q
- Bepul versiya yetarli

### Production uchun: VPS/Cloud
- DigitalOcean, AWS, Heroku
- Real domain bilan
- HTTPS sertifikat

---

## 📞 Qo'shimcha yordam

Agar hali ham ishlamasa:

1. **Firewall tekshirish:**
   - System Preferences > Security > Firewall
   - Status va settings ni screenshot qiling

2. **Network info:**
   ```bash
   ifconfig | grep "inet "
   netstat -an | grep 8000
   ```

3. **Server logs:**
   ```bash
   # Server loglarini kuzating
   python manage.py runserver 0.0.0.0:8000
   ```

---

**Eng oson: ngrok ishlatamiz! 🚀**

