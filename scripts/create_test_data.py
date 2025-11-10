#!/usr/bin/env python
"""
Create test data for SEW-TRACK project.
"""

import os
import django
from datetime import date, timedelta
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from apps.products.models import Product, ProductTask
from apps.tasks.models import Task, WorkRecord
from apps.employees.models import Employee

User = get_user_model()

print("🚀 Creating test data...")

# 1. Create Products
print("\n📦 Creating Products...")
products_data = [
    {"article_code": "ART-001", "name": "Ayollar ko'ylagi", "category": "womens"},
    {"article_code": "ART-002", "name": "Erkaklar ko'ylagi", "category": "mens"},
    {"article_code": "ART-003", "name": "Bolalar ko'ylagi", "category": "kids"},
]

products = {}
for data in products_data:
    product, created = Product.objects.get_or_create(
        article_code=data["article_code"],
        defaults={
            "name": data["name"],
            "category": data["category"],
            "is_active": True
        }
    )
    products[data["article_code"]] = product
    print(f"  {'✅ Created' if created else '   Exists'}: {product}")

# 2. Create Tasks
print("\n⚙️ Creating Tasks...")
tasks_data = [
    {"code": "TASK-001", "name_uz": "Tikish", "name_ru": "Шитье", "category": "sewing", "order": 1},
    {"code": "TASK-002", "name_uz": "Qirqish", "name_ru": "Резка", "category": "cutting", "order": 2},
    {"code": "TASK-003", "name_uz": "Dazmollash", "name_ru": "Глажка", "category": "ironing", "order": 3},
    {"code": "TASK-004", "name_uz": "Qadoqlash", "name_ru": "Упаковка", "category": "packaging", "order": 4},
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
    print(f"  {'✅ Created' if created else '   Exists'}: {task}")

# 3. Create ProductTasks (linking products to tasks with prices)
print("\n💰 Creating ProductTasks...")
product_tasks_data = [
    # ART-001 - Ayollar ko'ylagi
    {"product": "ART-001", "task": "TASK-001", "base_price": 5000, "minutes": 30},
    {"product": "ART-001", "task": "TASK-002", "base_price": 3000, "minutes": 15},
    {"product": "ART-001", "task": "TASK-003", "base_price": 2000, "minutes": 10},
    {"product": "ART-001", "task": "TASK-004", "base_price": 1000, "minutes": 5},
    # ART-002 - Erkaklar ko'ylagi
    {"product": "ART-002", "task": "TASK-001", "base_price": 6000, "minutes": 35},
    {"product": "ART-002", "task": "TASK-002", "base_price": 3500, "minutes": 20},
    {"product": "ART-002", "task": "TASK-003", "base_price": 2500, "minutes": 12},
    # ART-003 - Bolalar ko'ylagi
    {"product": "ART-003", "task": "TASK-001", "base_price": 4000, "minutes": 25},
    {"product": "ART-003", "task": "TASK-002", "base_price": 2500, "minutes": 12},
]

for data in product_tasks_data:
    pt, created = ProductTask.objects.get_or_create(
        product=products[data["product"]],
        task=tasks[data["task"]],
        defaults={
            "base_price": Decimal(data["base_price"]),
            "estimated_minutes": data["minutes"],
        }
    )
    print(f"  {'✅ Created' if created else '   Exists'}: {pt}")

# 4. Create/Update Employee for shahnoza user
print("\n👤 Creating Employee for shahnoza...")
try:
    user = User.objects.get(username='shahnoza')
    employee, created = Employee.objects.get_or_create(
        user=user,
        defaults={
            "full_name": "Shahnoza Karimova",
            "phone": "+998 91 921 70 41",
            "position": Employee.Position.WORKER,
            "employment_type": Employee.EmploymentType.FULL_TIME,
            "is_active": True,
            "hired_at": date.today() - timedelta(days=30),
        }
    )
    print(f"  {'✅ Created' if created else '   Exists'}: {employee}")
    
    # 5. Create some work records
    print("\n📝 Creating Work Records...")
    today = date.today()
    
    work_records_data = [
        {"product": "ART-001", "task": "TASK-001", "quantity": 10, "date": today},
        {"product": "ART-001", "task": "TASK-002", "quantity": 15, "date": today},
        {"product": "ART-002", "task": "TASK-001", "quantity": 8, "date": today - timedelta(days=1)},
        {"product": "ART-003", "task": "TASK-001", "quantity": 12, "date": today - timedelta(days=1)},
    ]
    
    for data in work_records_data:
        product = products[data["product"]]
        task = tasks[data["task"]]
        pt = ProductTask.objects.get(product=product, task=task)
        
        wr, created = WorkRecord.objects.get_or_create(
            employee=employee,
            product=product,
            task=task,
            work_date=data["date"],
            defaults={
                "product_task": pt,
                "quantity": data["quantity"],
                "price_per_unit": pt.get_price(),
                "total_payment": data["quantity"] * pt.get_price(),
                "status": WorkRecord.Status.PENDING,
            }
        )
        if created:
            print(f"  ✅ Created: {wr}")
        
except User.DoesNotExist:
    print("  ❌ User 'shahnoza' not found. Please create it first.")
    print("     Run: python manage.py shell -c \"from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_user(username='shahnoza', password='Password123!', is_active=True)\"")

print("\n✅ Test data creation completed!")
print("\n📊 Summary:")
print(f"  - Products: {Product.objects.count()}")
print(f"  - Tasks: {Task.objects.count()}")
print(f"  - ProductTasks: {ProductTask.objects.count()}")
print(f"  - Employees: {Employee.objects.count()}")
print(f"  - WorkRecords: {WorkRecord.objects.count()}")

