"""
URL patterns for Tasks app.
"""

from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    # Work Records
    path('work-records/', views.work_records_list, name='work_records_list'),
    path('work-records/create/', views.work_record_create, name='work_record_create'),
    path('work-records/<uuid:record_id>/', views.work_record_detail, name='work_record_detail'),
    
    # HTMX endpoints
    path('api/product/<uuid:product_id>/tasks/', views.get_product_tasks, name='get_product_tasks'),
    path('api/calculate-price/', views.calculate_price, name='calculate_price'),
]
