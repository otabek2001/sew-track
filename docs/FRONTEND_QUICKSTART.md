# 🚀 Frontend Quick Start Guide

## ✅ Nima amalga oshirildi?

### 1. **Mobile-First Web UI** (Django + HTMX + Alpine.js + Tailwind)

Yaratilgan sahifalar:
- ✅ Login page - `/login/`
- ✅ Dashboard - `/dashboard/`
- ✅ Statistics - `/statistics/`
- ✅ Profile - `/profile/`
- ✅ Base template (mobile navigation)

### 2. **Stack**
```
Backend:       Django 5.2 (mavjud)
Templates:     Django Templates
CSS:           Tailwind CSS 3 (CDN)
JS:            Alpine.js 3 (reactivity)
AJAX:          HTMX (dynamic updates)
Icons:         Lucide Icons
Charts:        Chart.js
```

### 3. **Features**
- ✅ Mobile-responsive (Tailwind CSS)
- ✅ Touch-optimized UI (44px+ touch targets)
- ✅ Bottom navigation (mobile)
- ✅ Real-time updates (HTMX)
- ✅ Interactive components (Alpine.js)
- ✅ Loading states & animations
- ✅ Toast notifications

---

## 🏃 Ishga Tushirish

### 1. Database Migration
```bash
cd /Users/otabeksayfullayev/PycharmProjects/sew-track
source venv/bin/activate
python manage.py migrate
```

### 2. Create Test User (agar yo'q bo'lsa)
```bash
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='shahnoza').exists():
    User.objects.create_user(
        username='shahnoza',
        password='Password123!',
        role=User.Role.WORKER,
        is_active=True
    )
    print('User created!')
else:
    print('User already exists')
"
```

### 3. Run Development Server
```bash
python manage.py runserver
```

### 4. Open in Browser
```
Login:    http://localhost:8000/login/
Username: shahnoza
Password: Password123!
```

---

## 📱 Test on Mobile

### Option 1: Local Network
```bash
# Find your IP
ifconfig | grep "inet " | grep -v 127.0.0.1

# Update ALLOWED_HOSTS in config/settings/development.py
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '192.168.1.X']

# Run server on 0.0.0.0
python manage.py runserver 0.0.0.0:8000

# Access from phone:
http://192.168.1.X:8000
```

### Option 2: ngrok (easiest)
```bash
# Install ngrok
brew install ngrok  # MacOS

# Run ngrok
ngrok http 8000

# Use the provided URL (e.g. https://abc123.ngrok.io)
```

---

## 📂 File Structure

```
sew-track/
├── apps/
│   └── dashboard/
│       ├── __init__.py
│       ├── apps.py
│       ├── views.py          # Dashboard views
│       └── urls.py           # URL patterns
├── templates/
│   ├── base.html             # Base template (mobile nav)
│   ├── dashboard.html        # Main dashboard
│   ├── statistics.html       # Statistics page
│   ├── profile.html          # User profile
│   ├── registration/
│   │   └── login.html        # Login page
│   └── dashboard/
│       └── _recent_tasks.html # HTMX partial
└── config/
    ├── urls.py               # Main URL config
    └── settings/
        └── base.py           # Updated settings
```

---

## 🎨 Tailwind CSS Classes

### Responsive Design
```html
<!-- Mobile-first approach -->
<div class="
  flex flex-col       <!-- Mobile: vertical stack -->
  md:flex-row         <!-- Tablet+: horizontal -->
  lg:space-x-8        <!-- Desktop: larger spacing -->
">
```

### Touch Targets
```html
<!-- Minimum 44px height for mobile -->
<button class="h-14 px-6 bg-blue-600 text-white rounded-lg">
  Save
</button>
```

### Cards
```html
<div class="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
  <!-- Content -->
</div>
```

---

## 🔄 HTMX Examples

### Load Content Dynamically
```html
<div 
  hx-get="/dashboard/recent-tasks/"
  hx-trigger="load"
  hx-target="this"
  hx-swap="innerHTML"
>
  <!-- Loading... -->
</div>
```

### Auto-refresh (TV Dashboard)
```html
<div 
  hx-get="/dashboard/stats/"
  hx-trigger="every 30s"
  hx-target="#stats"
>
  <!-- Stats content -->
</div>
```

---

## ⚡ Alpine.js Examples

### Toggle/Dropdown
```html
<div x-data="{ open: false }">
  <button @click="open = !open">Menu</button>
  <div x-show="open" @click.away="open = false">
    <!-- Dropdown content -->
  </div>
</div>
```

### Form with Calculation
```html
<form x-data="{ quantity: 0, price: 5000, total: 0 }">
  <input 
    type="number" 
    x-model="quantity"
    @input="total = quantity * price"
  >
  <p x-text="'Total: ' + total + ' so\'m'"></p>
</form>
```

---

## 📊 Chart.js Example

```html
<!-- Add Chart.js -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<canvas id="myChart"></canvas>

<script>
  new Chart(document.getElementById('myChart'), {
    type: 'line',
    data: {
      labels: ['Jan', 'Feb', 'Mar'],
      datasets: [{
        label: 'Sales',
        data: [12, 19, 3],
        borderColor: 'rgb(59, 130, 246)',
      }]
    }
  });
</script>
```

---

## 🐛 Troubleshooting

### Dashboard app not found
```bash
# Make sure dashboard is in INSTALLED_APPS
# config/settings/base.py
LOCAL_APPS = [
    ...
    'apps.dashboard',
]
```

### HTMX not loading
```html
<!-- Check if HTMX is loaded in base.html -->
<script src="https://unpkg.com/htmx.org@1.9.10"></script>
```

### Icons not showing
```html
<!-- Add Lucide initialization -->
<script>
  lucide.createIcons();
</script>
```

---

## 🎯 Next Steps

### 1. Create Work Records Form
```python
# apps/tasks/views.py
@login_required
def create_work_record(request):
    if request.method == 'POST':
        # Process form
        pass
    return render(request, 'tasks/create_work_record.html')
```

### 2. Add Task List
```python
@login_required
def task_list(request):
    tasks = Task.objects.filter(employee=request.user.employee)
    return render(request, 'tasks/list.html', {'tasks': tasks})
```

### 3. TV Dashboard
- Already created: `/dashboard/tv/`
- Features:
  - Auto-refresh (30s)
  - Real-time charts
  - KPI cards
  - Top performers

---

## 📱 Mobile UI Best Practices

### 1. Touch Targets
```css
/* Minimum 44x44px */
min-height: 44px;
min-width: 44px;
```

### 2. Font Sizes
```css
/* Minimum 16px to prevent zoom on iOS */
font-size: 16px;
```

### 3. Spacing
```css
/* Minimum 8px between interactive elements */
margin-bottom: 16px;
```

### 4. Safe Areas (iOS notch)
```css
padding-bottom: env(safe-area-inset-bottom);
```

---

## 🚀 Performance Tips

### 1. Lazy Load Images
```html
<img loading="lazy" src="image.jpg" alt="...">
```

### 2. Minimize CDN Resources
```html
<!-- Production: Self-host Tailwind -->
<link rel="stylesheet" href="{% static 'css/tailwind.css' %}">
```

### 3. HTMX Partial Views
```python
# Return only HTML fragment, not full page
def partial_view(request):
    return render(request, 'partials/_fragment.html')
```

---

## 📚 Resources

- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [HTMX Documentation](https://htmx.org/docs/)
- [Alpine.js Guide](https://alpinejs.dev/start-here)
- [Chart.js Examples](https://www.chartjs.org/docs/latest/samples/)
- [Lucide Icons](https://lucide.dev/icons/)

---

## ✅ Current Status

| Feature | Status | Notes |
|---------|--------|-------|
| Login Page | ✅ Complete | Mobile-optimized |
| Dashboard | ✅ Complete | Mock data |
| Statistics | ✅ Complete | Chart.js integrated |
| Profile | ✅ Complete | Settings page |
| Mobile Navigation | ✅ Complete | Bottom nav |
| HTMX Integration | ✅ Complete | Ready for partials |
| Alpine.js | ✅ Complete | Interactive components |
| Tailwind CSS | ✅ Complete | CDN (dev) |

---

## 🎯 Keyingi Qadamlar

1. ✅ ~~Login, Dashboard, Statistics, Profile sahifalari~~ (Tayyor!)
2. ⏳ Work Records CRUD
3. ⏳ Task Management
4. ⏳ Employee Management (Admin)
5. ⏳ TV Dashboard (Full)
6. ⏳ Real data integration

---

**Web UI tayyor! Mobile-first, responsive va zamonaviy! 🎉**

Davom ettiramizmi?

