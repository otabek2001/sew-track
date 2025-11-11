"""
URL patterns for Admin Panel app.
"""

from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    # Dashboard
    path('', views.admin_dashboard, name='dashboard'),
    
    # Tenant Management
    path('tenants/', views.tenant_list, name='tenant_list'),
    path('tenants/create/', views.tenant_create, name='tenant_create'),
    path('tenants/<uuid:tenant_id>/edit/', views.tenant_edit, name='tenant_edit'),
    path('tenants/switch/<uuid:tenant_id>/', views.switch_tenant, name='switch_tenant'),
    
    # Employee Management
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/create/', views.employee_create, name='employee_create'),
    path('employees/<uuid:employee_id>/edit/', views.employee_edit, name='employee_edit'),
    path('employees/<uuid:employee_id>/delete/', views.employee_delete, name='employee_delete'),
    
    # Product Management
    path('products/', views.product_list, name='product_list'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/<uuid:product_id>/edit/', views.product_edit, name='product_edit'),
    
    # Task Management
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/create/', views.task_create, name='task_create'),
    path('tasks/<uuid:task_id>/edit/', views.task_edit, name='task_edit'),
    
    # Product-Task Linking
    path('products/<uuid:product_id>/tasks/', views.product_tasks, name='product_tasks'),
    path('products/<uuid:product_id>/tasks/add/', views.product_task_add, name='product_task_add'),
    path('product-tasks/<uuid:product_task_id>/update/', views.product_task_update, name='product_task_update'),
    path('product-tasks/<uuid:product_task_id>/delete/', views.product_task_delete, name='product_task_delete'),
]

