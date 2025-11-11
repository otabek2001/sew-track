#!/usr/bin/env python
"""
Initialize multi-tenancy test data.

Creates:
- Superuser (owner)
- 2 Tenants (workshops)
- Employees, Products, Tasks for each tenant
- Sample work records
"""

import os
import sys
import django
from datetime import date, timedelta
from decimal import Decimal

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from apps.tenants.models import Tenant, TenantMembership
from apps.employees.models import Employee
from apps.products.models import Product, ProductTask
from apps.tasks.models import Task, WorkRecord

User = get_user_model()


def create_users_and_tenants():
    """Create owner and tenants."""
    print("\n🏗️  Creating Users and Tenants...")
    
    # Create superuser (owner)
    owner = User.objects.create_superuser(
        username='admin',
        email='admin@sewtrack.uz',
        password='admin123',
        role=User.Role.SUPER_ADMIN
    )
    print(f"✅ Created superuser: {owner.username}")
    
    # Create Tenant 1
    tenant1 = Tenant.objects.create(
        name='Oltin Ipak',
        slug='oltin-ipak',
        owner=owner,
        address='Toshkent sh., Chilonzor tumani',
        phone='+998901234567',
        email='oltin@example.com',
        is_active=True
    )
    print(f"✅ Created tenant: {tenant1.name}")
    
    # Create Tenant 2
    tenant2 = Tenant.objects.create(
        name='Bahor Tikuvchilik',
        slug='bahor',
        owner=owner,
        address='Samarqand sh., Markaz tumani',
        phone='+998909876543',
        email='bahor@example.com',
        is_active=True
    )
    print(f"✅ Created tenant: {tenant2.name}")
    
    # Create membership for owner
    TenantMembership.objects.create(
        tenant=tenant1,
        user=owner,
        role=TenantMembership.Role.OWNER,
        is_active=True
    )
    TenantMembership.objects.create(
        tenant=tenant2,
        user=owner,
        role=TenantMembership.Role.OWNER,
        is_active=True
    )
    print("✅ Created tenant memberships")
    
    return owner, tenant1, tenant2


def create_employees(tenant):
    """Create test employees for a tenant."""
    print(f"\n👥 Creating Employees for {tenant.name}...")
    
    employees_data = [
        # Masters
        {
            'username': f'master1_{tenant.slug}',
            'full_name': 'Alisher Rahimov',
            'position': Employee.Position.MASTER,
            'role': User.Role.MASTER,
        },
        # Workers
        {
            'username': f'worker1_{tenant.slug}',
            'full_name': 'Dilnoza Tursunova',
            'position': Employee.Position.WORKER,
            'role': User.Role.WORKER,
        },
        {
            'username': f'worker2_{tenant.slug}',
            'full_name': 'Malika Saidova',
            'position': Employee.Position.WORKER,
            'role': User.Role.WORKER,
        },
        {
            'username': f'worker3_{tenant.slug}',
            'full_name': 'Rustam Aminov',
            'position': Employee.Position.WORKER,
            'role': User.Role.WORKER,
        },
    ]
    
    employees = []
    for emp_data in employees_data:
        # Create user
        user = User.objects.create_user(
            username=emp_data['username'],
            password='password123',
            role=emp_data['role']
        )
        
        # Create employee
        employee = Employee.objects.create(
            tenant=tenant,
            user=user,
            full_name=emp_data['full_name'],
            phone='+998901234567',
            position=emp_data['position'],
            employment_type=Employee.EmploymentType.FULL_TIME,
            hourly_rate=Decimal('15000.00'),
            is_active=True,
            hired_at=date.today() - timedelta(days=30)
        )
        employees.append(employee)
        print(f"  ✅ {employee.full_name} ({employee.get_position_display()})")
    
    return employees


def create_products(tenant):
    """Create test products for a tenant."""
    print(f"\n📦 Creating Products for {tenant.name}...")
    
    products_data = [
        {'code': 'ART-001', 'name': 'Ayollar shim', 'category': Product.Category.WOMENS},
        {'code': 'ART-002', 'name': 'Erkaklar shim', 'category': Product.Category.MENS},
        {'code': 'ART-003', 'name': 'Bolalar ko\'ylagi', 'category': Product.Category.KIDS},
        {'code': 'ART-004', 'name': 'Женский костюм (юбка)', 'category': Product.Category.WOMENS},
    ]
    
    products = []
    for prod_data in products_data:
        product = Product.objects.create(
            tenant=tenant,
            article_code=f"{prod_data['code']}-{tenant.slug}",
            name=prod_data['name'],
            category=prod_data['category'],
            is_active=True
        )
        products.append(product)
        print(f"  ✅ {product.article_code} - {product.name}")
    
    return products


def create_tasks(tenant):
    """Create test tasks for a tenant."""
    print(f"\n⚙️  Creating Tasks for {tenant.name}...")
    
    tasks_data = [
        {'code': 'TASK-001', 'name_uz': 'Tikish', 'name_ru': 'Шитье', 'category': Task.Category.SEWING},
        {'code': 'TASK-002', 'name_uz': 'Kesish', 'name_ru': 'Резка', 'category': Task.Category.CUTTING},
        {'code': 'TASK-003', 'name_uz': 'Dazmollash', 'name_ru': 'Глажка', 'category': Task.Category.IRONING},
        {'code': 'TASK-004', 'name_uz': 'Sifat nazorati', 'name_ru': 'Контроль качества', 'category': Task.Category.QUALITY_CHECK},
        {'code': 'TASK-005', 'name_uz': 'Orqa relf lenta yopish', 'name_ru': 'Приклейка ленты', 'category': Task.Category.SEWING},
    ]
    
    tasks = []
    for idx, task_data in enumerate(tasks_data):
        task = Task.objects.create(
            tenant=tenant,
            code=f"{task_data['code']}-{tenant.slug}",
            name_uz=task_data['name_uz'],
            name_ru=task_data['name_ru'],
            category=task_data['category'],
            sequence_order=idx + 1,
            is_active=True
        )
        tasks.append(task)
        print(f"  ✅ {task.code} - {task.name_uz}")
    
    return tasks


def create_product_tasks(products, tasks):
    """Link products with tasks and set prices."""
    print("\n🔗 Creating ProductTask links...")
    
    count = 0
    for product in products:
        for task in tasks:
            # Create link with random price
            base_price = Decimal('5000.00') if task.category == Task.Category.SEWING else Decimal('3000.00')
            
            ProductTask.objects.create(
                product=product,
                task=task,
                base_price=base_price,
                premium_price=base_price * Decimal('1.5'),
                price_type=ProductTask.PriceType.BASE,
                estimated_minutes=30
            )
            count += 1
    
    print(f"  ✅ Created {count} product-task links")


def create_work_records(tenant, employees, products, tasks):
    """Create sample work records."""
    print(f"\n📝 Creating Work Records for {tenant.name}...")
    
    count = 0
    today = date.today()
    
    # Create records for last 3 days
    for day_offset in range(3):
        work_date = today - timedelta(days=day_offset)
        
        # Each worker creates 2-3 records per day
        for employee in employees:
            if employee.position != Employee.Position.MASTER:
                num_records = 2 if day_offset > 0 else 3
                
                for _ in range(num_records):
                    product = products[count % len(products)]
                    task = tasks[count % len(tasks)]
                    
                    # Get ProductTask
                    product_task = ProductTask.objects.filter(
                        product=product,
                        task=task
                    ).first()
                    
                    if product_task:
                        quantity = (count % 20) + 10  # 10-30
                        
                        WorkRecord.objects.create(
                            tenant=tenant,
                            employee=employee,
                            product=product,
                            task=task,
                            product_task=product_task,
                            quantity=quantity,
                            price_per_unit=product_task.base_price,
                            total_payment=quantity * product_task.base_price,
                            work_date=work_date,
                            status=WorkRecord.Status.PENDING if day_offset == 0 else WorkRecord.Status.APPROVED,
                            notes='Test record'
                        )
                        count += 1
    
    print(f"  ✅ Created {count} work records")


def main():
    """Main function."""
    print("="*60)
    print("🚀 INITIALIZING MULTI-TENANCY TEST DATA")
    print("="*60)
    
    # Create users and tenants
    owner, tenant1, tenant2 = create_users_and_tenants()
    
    # For each tenant
    for tenant in [tenant1, tenant2]:
        print(f"\n{'='*60}")
        print(f"🏭 TENANT: {tenant.name}")
        print(f"{'='*60}")
        
        # Create data
        employees = create_employees(tenant)
        products = create_products(tenant)
        tasks = create_tasks(tenant)
        create_product_tasks(products, tasks)
        create_work_records(tenant, employees, products, tasks)
    
    print("\n" + "="*60)
    print("✅ DATA INITIALIZATION COMPLETE!")
    print("="*60)
    print(f"\n📊 Summary:")
    print(f"  - Tenants: {Tenant.objects.count()}")
    print(f"  - Users: {User.objects.count()}")
    print(f"  - Employees: {Employee.objects.count()}")
    print(f"  - Products: {Product.objects.count()}")
    print(f"  - Tasks: {Task.objects.count()}")
    print(f"  - ProductTasks: {ProductTask.objects.count()}")
    print(f"  - WorkRecords: {WorkRecord.objects.count()}")
    
    print(f"\n🔑 Login Credentials:")
    print(f"  Superuser: admin / admin123")
    print(f"  Master 1: master1_oltin-ipak / password123")
    print(f"  Master 2: master1_bahor / password123")
    print(f"  Worker 1: worker1_oltin-ipak / password123")
    print(f"  Worker 2: worker2_oltin-ipak / password123")
    
    print("\n")


if __name__ == '__main__':
    main()

