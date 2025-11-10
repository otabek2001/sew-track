"""
Master/Admin views for work record approval workflow.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Sum, Count
from django.utils import timezone
from django.contrib import messages
from datetime import date, timedelta

from apps.tasks.models import WorkRecord
from apps.employees.models import Employee
from apps.products.models import Product
from apps.tasks.models import Task


def is_master_or_admin(user):
    """Check if user is master or admin."""
    return user.is_staff or (
        hasattr(user, 'employee') and 
        user.employee.position in [Employee.Position.MASTER, Employee.Position.SUPERVISOR]
    ) or user.is_master_or_above


@login_required
@user_passes_test(is_master_or_admin, login_url='/dashboard/')
def master_dashboard(request):
    """
    Master dashboard - overview and quick stats.
    """
    today = date.today()
    
    # Statistics
    pending_count = WorkRecord.objects.filter(status=WorkRecord.Status.PENDING).count()
    today_approved = WorkRecord.objects.filter(
        work_date=today,
        status=WorkRecord.Status.APPROVED
    ).count()
    today_rejected = WorkRecord.objects.filter(
        work_date=today,
        status=WorkRecord.Status.REJECTED
    ).count()
    
    # Recent activity (last 10 approved/rejected)
    recent_activity = WorkRecord.objects.filter(
        status__in=[WorkRecord.Status.APPROVED, WorkRecord.Status.REJECTED]
    ).select_related(
        'employee', 'product', 'task'
    ).order_by('-updated_at')[:10]
    
    stats = {
        'pending_count': pending_count,
        'today_approved': today_approved,
        'today_rejected': today_rejected,
    }
    
    return render(request, 'master/dashboard.html', {
        'stats': stats,
        'recent_activity': recent_activity,
    })


@login_required
@user_passes_test(is_master_or_admin, login_url='/dashboard/')
def pending_approvals(request):
    """
    List of pending work records for approval.
    With filters and bulk operations.
    """
    # Get filter parameters
    date_filter = request.GET.get('date', 'all')
    employee_filter = request.GET.get('employee', '')
    product_filter = request.GET.get('product', '')
    
    # Base query - only pending
    records = WorkRecord.objects.filter(
        status=WorkRecord.Status.PENDING
    ).select_related(
        'employee', 'product', 'task', 'product_task'
    )
    
    # Date filter
    today = date.today()
    if date_filter == 'today':
        records = records.filter(work_date=today)
    elif date_filter == 'week':
        week_start = today - timedelta(days=today.weekday())
        records = records.filter(work_date__gte=week_start)
    elif date_filter == 'month':
        records = records.filter(
            work_date__year=today.year,
            work_date__month=today.month
        )
    
    # Employee filter
    if employee_filter:
        records = records.filter(employee_id=employee_filter)
    
    # Product filter
    if product_filter:
        records = records.filter(product_id=product_filter)
    
    # Statistics for filtered records
    stats = records.aggregate(
        total_quantity=Sum('quantity'),
        total_payment=Sum('total_payment'),
        count=Count('id')
    )
    
    # Order by date (newest first)
    records = records.order_by('-work_date', '-created_at')
    
    # Get filter options
    employees = Employee.objects.filter(is_active=True).order_by('full_name')
    products = Product.objects.filter(is_active=True).order_by('article_code')
    
    return render(request, 'master/pending_approvals.html', {
        'records': records,
        'stats': stats,
        'date_filter': date_filter,
        'employee_filter': employee_filter,
        'product_filter': product_filter,
        'employees': employees,
        'products': products,
    })


@login_required
@user_passes_test(is_master_or_admin, login_url='/dashboard/')
def approve_record(request, record_id):
    """
    Approve single work record.
    """
    if request.method == 'POST':
        record = get_object_or_404(WorkRecord, id=record_id, status=WorkRecord.Status.PENDING)
        
        # Get approver (current user's employee)
        approver = None
        if hasattr(request.user, 'employee'):
            approver = request.user.employee
        
        # Approve record
        record.approve(approver)
        
        # HTMX response
        if request.headers.get('HX-Request'):
            return HttpResponse(
                '<div class="bg-green-50 text-green-700 p-2 rounded">✅ Tasdiqlandi</div>',
                headers={'HX-Trigger': 'recordUpdated'}
            )
        
        messages.success(request, 'Yozuv muvaffaqiyatli tasdiqlandi!')
        return redirect('master:pending_approvals')
    
    return redirect('master:pending_approvals')


@login_required
@user_passes_test(is_master_or_admin, login_url='/dashboard/')
def reject_record(request, record_id):
    """
    Reject single work record.
    """
    if request.method == 'POST':
        record = get_object_or_404(WorkRecord, id=record_id, status=WorkRecord.Status.PENDING)
        
        # Get reject reason (optional)
        reason = request.POST.get('reason', '')
        if reason:
            record.notes = f"Rad etildi: {reason}"
        
        # Reject record
        record.reject()
        
        # HTMX response
        if request.headers.get('HX-Request'):
            return HttpResponse(
                '<div class="bg-red-50 text-red-700 p-2 rounded">❌ Rad etildi</div>',
                headers={'HX-Trigger': 'recordUpdated'}
            )
        
        messages.warning(request, 'Yozuv rad etildi.')
        return redirect('master:pending_approvals')
    
    return redirect('master:pending_approvals')


@login_required
@user_passes_test(is_master_or_admin, login_url='/dashboard/')
def bulk_approve(request):
    """
    Bulk approve multiple work records.
    """
    if request.method == 'POST':
        record_ids = request.POST.getlist('record_ids')
        
        if not record_ids:
            messages.warning(request, 'Hech qanday yozuv tanlanmadi!')
            return redirect('master:pending_approvals')
        
        # Get approver
        approver = None
        if hasattr(request.user, 'employee'):
            approver = request.user.employee
        
        # Approve all selected records
        count = 0
        for record_id in record_ids:
            try:
                record = WorkRecord.objects.get(id=record_id, status=WorkRecord.Status.PENDING)
                record.approve(approver)
                count += 1
            except WorkRecord.DoesNotExist:
                continue
        
        messages.success(request, f'{count} ta yozuv tasdiqlandi!')
        return redirect('master:pending_approvals')
    
    return redirect('master:pending_approvals')


@login_required
@user_passes_test(is_master_or_admin, login_url='/dashboard/')
def bulk_reject(request):
    """
    Bulk reject multiple work records.
    """
    if request.method == 'POST':
        record_ids = request.POST.getlist('record_ids')
        reason = request.POST.get('reason', '')
        
        if not record_ids:
            messages.warning(request, 'Hech qanday yozuv tanlanmadi!')
            return redirect('master:pending_approvals')
        
        # Reject all selected records
        count = 0
        for record_id in record_ids:
            try:
                record = WorkRecord.objects.get(id=record_id, status=WorkRecord.Status.PENDING)
                if reason:
                    record.notes = f"Rad etildi: {reason}"
                record.reject()
                count += 1
            except WorkRecord.DoesNotExist:
                continue
        
        messages.warning(request, f'{count} ta yozuv rad etildi.')
        return redirect('master:pending_approvals')
    
    return redirect('master:pending_approvals')


@login_required
@user_passes_test(is_master_or_admin, login_url='/dashboard/')
def work_record_detail_master(request, record_id):
    """
    Work record detail view for master (with approve/reject options).
    """
    record = get_object_or_404(WorkRecord, id=record_id)
    
    return render(request, 'master/record_detail.html', {
        'record': record,
    })

