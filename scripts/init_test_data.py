"""
Script to initialize test data for SEW-TRACK.

Run with: python scripts/init_test_data.py
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from datetime import date
from django.contrib.auth import get_user_model
from apps.employees.models import Employee
from apps.tasks.models import Task
from apps.products.models import Product, ProductTask

User = get_user_model()


def create_test_tasks():
    """Create test tasks."""
    tasks_data = [
        {
            'code': 'TASK-001',
            'name_uz': 'Олди релф лента ёпиштириш',
            'name_ru': 'Приклеивание передней рельефной ленты',
            'category': Task.Category.SEWING,
            'sequence_order': 1,
        },
        {
            'code': 'TASK-002',
            'name_uz': 'Орқа релф лента ёпиштириш',
            'name_ru': 'Приклеивание задней рельефной ленты',
            'category': Task.Category.SEWING,
            'sequence_order': 2,
        },
        {
            'code': 'TASK-003',
            'name_uz': 'Елка тикиш',
            'name_ru': 'Пошив юбки',
            'category': Task.Category.SEWING,
            'sequence_order': 3,
        },
        {
            'code': 'TASK-004',
            'name_uz': 'Пиджак тикиш',
            'name_ru': 'Пошив пиджака',
            'category': Task.Category.SEWING,
            'sequence_order': 4,
        },
        {
            'code': 'TASK-005',
            'name_uz': 'Дазмоллаш',
            'name_ru': 'Глажение',
            'category': Task.Category.IRONING,
            'sequence_order': 5,
        },
    ]
    
    created = 0
    for task_data in tasks_data:
        task, created_flag = Task.objects.get_or_create(
            code=task_data['code'],
            defaults=task_data
        )
        if created_flag:
            print(f'✅ Created task: {task.code} - {task.name_uz}')
            created += 1
        else:
            print(f'ℹ️ Task already exists: {task.code}')
    
    print(f'\n📊 Tasks: {created} created, {Task.objects.count()} total\n')


def create_test_products():
    """Create test products."""
    products_data = [
        {
            'article_code': 'ART-034',
            'name': 'Женский костюм (юбка)',
            'category': Product.Category.WOMENS,
        },
        {
            'article_code': 'ART-035',
            'name': 'Женский костюм (пиджак)',
            'category': Product.Category.WOMENS,
        },
        {
            'article_code': 'ART-036',
            'name': 'Мужской костюм',
            'category': Product.Category.MENS,
        },
    ]
    
    created = 0
    for product_data in products_data:
        product, created_flag = Product.objects.get_or_create(
            article_code=product_data['article_code'],
            defaults=product_data
        )
        if created_flag:
            print(f'✅ Created product: {product.article_code} - {product.name}')
            created += 1
        else:
            print(f'ℹ️ Product already exists: {product.article_code}')
    
    print(f'\n📊 Products: {created} created, {Product.objects.count()} total\n')


def create_product_tasks():
    """Link products with tasks and set prices."""
    
    # Get products and tasks
    skirt = Product.objects.get(article_code='ART-034')
    jacket = Product.objects.get(article_code='ART-035')
    
    task_001 = Task.objects.get(code='TASK-001')
    task_002 = Task.objects.get(code='TASK-002')
    task_003 = Task.objects.get(code='TASK-003')
    task_005 = Task.objects.get(code='TASK-005')
    
    product_tasks_data = [
        # Skirt operations
        {'product': skirt, 'task': task_001, 'base_price': 450, 'estimated_minutes': 15},
        {'product': skirt, 'task': task_002, 'base_price': 450, 'estimated_minutes': 15},
        {'product': skirt, 'task': task_003, 'base_price': 800, 'estimated_minutes': 30},
        {'product': skirt, 'task': task_005, 'base_price': 200, 'estimated_minutes': 10},
        
        # Jacket operations
        {'product': jacket, 'task': task_001, 'base_price': 500, 'estimated_minutes': 20},
        {'product': jacket, 'task': task_002, 'base_price': 500, 'estimated_minutes': 20},
    ]
    
    created = 0
    for pt_data in product_tasks_data:
        pt, created_flag = ProductTask.objects.get_or_create(
            product=pt_data['product'],
            task=pt_data['task'],
            defaults={
                'base_price': pt_data['base_price'],
                'estimated_minutes': pt_data['estimated_minutes'],
            }
        )
        if created_flag:
            print(f'✅ Linked: {pt.product.article_code} + {pt.task.code} = {pt.base_price} UZS')
            created += 1
    
    print(f'\n📊 ProductTasks: {created} created, {ProductTask.objects.count()} total\n')


def main():
    """Main function."""
    print('🚀 Initializing test data for SEW-TRACK...\n')
    
    print('=' * 60)
    print('1️⃣ Creating Tasks...')
    print('=' * 60)
    create_test_tasks()
    
    print('=' * 60)
    print('2️⃣ Creating Products...')
    print('=' * 60)
    create_test_products()
    
    print('=' * 60)
    print('3️⃣ Linking Products with Tasks...')
    print('=' * 60)
    create_product_tasks()
    
    print('=' * 60)
    print('✅ Test data initialization completed!')
    print('=' * 60)


if __name__ == '__main__':
    main()

