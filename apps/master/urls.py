"""
URL patterns for Master app.
"""

from django.urls import path
from . import views

app_name = 'master'

urlpatterns = [
    # Master Dashboard
    path('', views.master_dashboard, name='dashboard'),
    
    # Pending Approvals
    path('pending/', views.pending_approvals, name='pending_approvals'),
    path('pending-simple/', lambda request: __import__('django.shortcuts').shortcuts.render(request, 'master/pending_simple.html', {
        'records': __import__('apps.tasks.models').tasks.models.WorkRecord.objects.filter(status='pending').select_related('employee', 'product', 'task')[:20],
        'stats': {'count': __import__('apps.tasks.models').tasks.models.WorkRecord.objects.filter(status='pending').count()},
        'date_filter': 'all'
    }), name='pending_simple'),
    path('record/<uuid:record_id>/', views.work_record_detail_master, name='record_detail'),
    
    # Single Actions
    path('approve/<uuid:record_id>/', views.approve_record, name='approve_record'),
    path('reject/<uuid:record_id>/', views.reject_record, name='reject_record'),
    
    # Bulk Actions
    path('bulk-approve/', views.bulk_approve, name='bulk_approve'),
    path('bulk-reject/', views.bulk_reject, name='bulk_reject'),
]

