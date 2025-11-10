#!/usr/bin/env python
"""
Create realistic demo/test data for SEW-TRACK project.
Professional data for demo and testing.
"""

import os
import django
from datetime import date, timedelta
from decimal import Decimal
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from django.db.models import Sum, Count
from apps.products.models import Product, ProductTask
from apps.tasks.models import Task, WorkRecord
from apps.employees.models import Employee

User = get_user_model()

print("🚀 Creating comprehensive demo data for SEW-TRACK...")
print("=" * 60)

# ============================================================
# 1. USERS & EMPLOYEES
# ============================================================
print("\n👥 Creating Users and Employees...")

employees_data = [
    {"username": "shahnoza", "full_name": "Shahnoza Karimova", "phone": "+998 91 921 70 41", "position": "worker"},
    {"username": "fatima", "full_name": "Fatima Alimova", "phone": "+998 90 123 45 67", "position": "worker"},
    {"username": "dilnoza", "full_name": "Dilnoza Tursunova", "phone": "+998 93 234 56 78", "position": "worker"},
    {"username": "malika", "full_name": "Malika Saidova", "phone": "+998 94 345 67 89", "position": "worker"},
    {"username": "nodira", "full_name": "Nodira Rashidova", "phone": "+998 95 456 78 90", "position": "worker"},
    {"username": "zilola", "full_name": "Zilola Azimova", "phone": "+998 97 567 89 01", "position": "worker"},
    {"username": "sevara", "full_name": "Sevara Mahmudova", "phone": "+998 98 678 90 12", "position": "worker"},
    {"username": "gulnora", "full_name": "Gulnora Yusupova", "phone": "+998 99 789 01 23", "position": "worker"},
    {"username": "dilfuza", "full_name": "Dilfuza Hamidova", "phone": "+998 90 890 12 34", "position": "worker"},
    {"username": "munira", "full_name": "Munira Karimova", "phone": "+998 91 901 23 45", "position": "worker"},
    {"username": "rustam", "full_name": "Rustam Aminov", "phone": "+998 93 012 34 56", "position": "master"},
    {"username": "jasur", "full_name": "Jasur Toshmatov", "phone": "+998 94 123 45 67", "position": "supervisor"},
]

employees = {}
for emp_data in employees_data:
    # Create or get user
    user, user_created = User.objects.get_or_create(
        username=emp_data["username"],
        defaults={
            "is_active": True,
            "role": User.Role.WORKER if emp_data["position"] == "worker" else User.Role.MASTER,
        }
    )
    
    if user_created:
        user.set_password("Password123!")
        user.save()
        print(f"  ✅ User created: {emp_data['username']}")
    else:
        print(f"     Exists: {emp_data['username']}")
    
    # Create or get employee
    employee, emp_created = Employee.objects.get_or_create(
        user=user,
        defaults={
            "full_name": emp_data["full_name"],
            "phone": emp_data["phone"],
            "position": emp_data["position"],
            "employment_type": Employee.EmploymentType.FULL_TIME,
            "is_active": True,
            "hired_at": date.today() - timedelta(days=random.randint(30, 365)),
        }
    )
    
    employees[emp_data["username"]] = employee
    if emp_created:
        print(f"  ✅ Employee created: {emp_data['full_name']}")

# ============================================================
# 2. PRODUCTS
# ============================================================
print("\n📦 Creating Products...")

products_data = [
    {"code": "ART-001", "name": "Ayollar yozgi ko'ylagi", "category": "womens"},
    {"code": "ART-002", "name": "Erkaklar ko'ylagi", "category": "mens"},
    {"code": "ART-003", "name": "Bolalar ko'ylagi", "category": "kids"},
    {"code": "ART-004", "name": "Ayollar shim", "category": "womens"},
    {"code": "ART-005", "name": "Erkaklar shim", "category": "mens"},
    {"code": "ART-006", "name": "Ayollar ko'ylak", "category": "womens"},
    {"code": "ART-007", "name": "Bolalar sport kiyimi", "category": "kids"},
]

products = {}
for data in products_data:
    product, created = Product.objects.get_or_create(
        article_code=data["code"],
        defaults={
            "name": data["name"],
            "category": data["category"],
            "is_active": True
        }
    )
    products[data["code"]] = product
    print(f"  {'✅ Created' if created else '   Exists'}: {product}")

# ============================================================
# 3. TASKS (Operations)
# ============================================================
print("\n⚙️ Creating Tasks...")

tasks_data = [
    {"code": "OP-001", "name_uz": "Qirqish", "name_ru": "Резка", "category": "cutting", "order": 1},
    {"code": "OP-002", "name_uz": "Tikish", "name_ru": "Шитье", "category": "sewing", "order": 2},
    {"code": "OP-003", "name_uz": "Yoqa tikish", "name_ru": "Пошив воротника", "category": "sewing", "order": 3},
    {"code": "OP-004", "name_uz": "Yeng tikish", "name_ru": "Пошив рукава", "category": "sewing", "order": 4},
    {"code": "OP-005", "name_uz": "Tugma tikish", "name_ru": "Пришивка пуговиц", "category": "sewing", "order": 5},
    {"code": "OP-006", "name_uz": "Dazmollash", "name_ru": "Глажка", "category": "ironing", "order": 6},
    {"code": "OP-007", "name_uz": "Sifat nazorati", "name_ru": "Контроль качества", "category": "quality_check", "order": 7},
    {"code": "OP-008", "name_uz": "Qadoqlash", "name_ru": "Упаковка", "category": "packaging", "order": 8},
]

tasks = {}
for data in tasks_data:
    task, created = Task.objects.get_or_create(
        code=data["code"],
        defaults={
            "name_uz": data["name_uz"],
            "name_ru": data["name_ru"],
            "category": data["category"],
            "sequence_order": data["order"],
            "is_active": True
        }
    )
    tasks[data["code"]] = task
    if created:
        print(f"  ✅ Created: {task}")

# ============================================================
# 4. PRODUCT-TASK PRICING
# ============================================================
print("\n💰 Creating ProductTask pricing...")

# Price ranges for different operations
price_ranges = {
    "OP-001": (2000, 3000),   # Qirqish
    "OP-002": (5000, 7000),   # Tikish (main)
    "OP-003": (3000, 4000),   # Yoqa
    "OP-004": (2500, 3500),   # Yeng
    "OP-005": (1000, 1500),   # Tugma
    "OP-006": (2000, 2500),   # Dazmol
    "OP-007": (1500, 2000),   # Sifat
    "OP-008": (1000, 1500),   # Qadoq
}

count = 0
for product_code, product in products.items():
    # Each product has 4-6 operations
    operations = random.sample(list(tasks.keys()), random.randint(4, 6))
    
    for task_code in operations:
        task = tasks[task_code]
        price_min, price_max = price_ranges.get(task_code, (2000, 5000))
        base_price = random.randint(price_min, price_max)
        
        pt, created = ProductTask.objects.get_or_create(
            product=product,
            task=task,
            defaults={
                "base_price": Decimal(base_price),
                "estimated_minutes": random.randint(10, 45),
            }
        )
        if created:
            count += 1

print(f"  ✅ Created {count} ProductTask entries")

# ============================================================
# 5. WORK RECORDS (Realistic data for last 7 days)
# ============================================================
print("\n📝 Creating Work Records (last 7 days)...")

today = date.today()
created_count = 0

# Get all product-tasks
all_product_tasks = list(ProductTask.objects.all().select_related('product', 'task'))

if not all_product_tasks:
    print("  ❌ No ProductTasks found! Please run basic setup first.")
else:
    # For each day in last 7 days
    for days_ago in range(7):
        work_day = today - timedelta(days=days_ago)
        
        # Weekend - less work
        is_weekend = work_day.weekday() >= 5
        num_workers = random.randint(3, 6) if is_weekend else random.randint(8, 12)
        
        # Random workers for this day
        day_workers = random.sample(list(employees.values()), num_workers)
        
        for employee in day_workers:
            # Each worker does 2-5 tasks per day
            num_tasks = random.randint(1, 3) if is_weekend else random.randint(2, 5)
            
            # Random product-tasks
            worker_tasks = random.sample(all_product_tasks, min(num_tasks, len(all_product_tasks)))
            
            for pt in worker_tasks:
                # Random quantity (realistic)
                quantity = random.randint(5, 30)
                
                # Random status (realistic distribution)
                status_choice = random.choices(
                    [WorkRecord.Status.PENDING, WorkRecord.Status.COMPLETED, WorkRecord.Status.APPROVED, WorkRecord.Status.REJECTED],
                    weights=[20, 30, 45, 5],  # Most approved, some completed, few pending, rare rejected
                    k=1
                )[0]
                
                # Don't create duplicate records
                existing = WorkRecord.objects.filter(
                    employee=employee,
                    product=pt.product,
                    task=pt.task,
                    work_date=work_day
                ).exists()
                
                if not existing:
                    wr = WorkRecord.objects.create(
                        employee=employee,
                        product=pt.product,
                        task=pt.task,
                        product_task=pt,
                        quantity=quantity,
                        price_per_unit=pt.get_price(),
                        total_payment=quantity * pt.get_price(),
                        work_date=work_day,
                        status=status_choice,
                    )
                    created_count += 1

print(f"  ✅ Created {created_count} WorkRecord entries")

# ============================================================
# 6. SUMMARY
# ============================================================
print("\n" + "=" * 60)
print("✅ Demo data creation completed!")
print("=" * 60)
print("\n📊 Database Summary:")
print(f"  - Users:         {User.objects.count()}")
print(f"  - Employees:     {Employee.objects.count()}")
print(f"  - Products:      {Product.objects.count()}")
print(f"  - Tasks:         {Task.objects.count()}")
print(f"  - ProductTasks:  {ProductTask.objects.count()}")
print(f"  - WorkRecords:   {WorkRecord.objects.count()}")

# Statistics
today_records = WorkRecord.objects.filter(work_date=today)
print(f"\n📈 Today's Statistics:")
print(f"  - Records:       {today_records.count()}")
print(f"  - Active Workers: {today_records.values('employee').distinct().count()}")
print(f"  - Total Quantity: {today_records.aggregate(total=Sum('quantity'))['total'] or 0}")
print(f"  - Total Payment:  {today_records.aggregate(total=Sum('total_payment'))['total'] or 0:,.0f} so'm")

# Status breakdown
from django.db.models import Sum, Count
status_breakdown = WorkRecord.objects.values('status').annotate(
    count=Count('id'),
    total=Sum('total_payment')
).order_by('-count')

print(f"\n📊 Work Records by Status:")
for item in status_breakdown:
    print(f"  - {item['status']:12} {item['count']:3} records  {item['total'] or 0:>10,.0f} so'm")

# Top performers
print(f"\n🏆 Top 5 Performers (All Time):")
top = WorkRecord.objects.values('employee__full_name').annotate(
    total_quantity=Sum('quantity'),
    total_payment=Sum('total_payment')
).order_by('-total_quantity')[:5]

for i, performer in enumerate(top, 1):
    medal = ["🥇", "🥈", "🥉", "  ", "  "][i-1]
    print(f"  {medal} {i}. {performer['employee__full_name']:25} {performer['total_quantity']:3} dona  {performer['total_payment']:>10,.0f} so'm")

print("\n" + "=" * 60)
print("🎉 Demo data ready! Test the application now!")
print("=" * 60)
print("\n🌐 URLs:")
print("  Worker:  http://localhost:8000/login/")
print("  TV:      http://localhost:8000/dashboard/tv/")
print("  Admin:   http://localhost:8000/admin/")
print("\n👤 Login credentials:")
print("  Username: shahnoza (or any from above)")
print("  Password: Password123!")
print("\n🎯 Test TV Dashboard - should see real ranking!")

