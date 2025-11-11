"""
Dashboard views with mobile-first design.
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta
import json

from apps.accounts.models import User
from apps.tasks.models import Task, WorkRecord
from apps.employees.models import Employee


@login_required
def dashboard(request):
    """
    Main dashboard view for worker role.
    Mobile-optimized with quick stats and recent activity.
    Admin users are redirected to admin panel.
    """
    user = request.user
    
    # Redirect admin users to admin panel
    if user.role in [User.Role.SUPER_ADMIN, User.Role.TENANT_ADMIN]:
        return redirect('admin_panel:dashboard')
    
    # Redirect masters to master panel
    if user.role == User.Role.MASTER:
        return redirect('master:dashboard')
    
    today = date.today()
    
    # Default stats
    stats = {
        'today_tasks': 0,
        'completed': 0,
        'in_progress': 0,
        'earnings': 0,
    }
    
    # Get real data if user has employee record
    if hasattr(user, 'employee'):
        employee = user.employee
        
        # Today's statistics
        today_records = WorkRecord.objects.filter(
            employee=employee,
            work_date=today
        )
        
        stats = {
            'today_tasks': today_records.count(),
            'completed': today_records.filter(
                status__in=[WorkRecord.Status.COMPLETED, WorkRecord.Status.APPROVED]
            ).count(),
            'in_progress': today_records.filter(
                status=WorkRecord.Status.PENDING
            ).count(),
            'earnings': today_records.aggregate(
                total=Sum('total_payment')
            )['total'] or 0,
        }
    
    return render(request, 'dashboard.html', {
        'stats': stats,
    })


@login_required
def recent_tasks(request):
    """
    HTMX partial view for recent tasks (worker dashboard only).
    Returns only the HTML fragment for dynamic loading.
    """
    user = request.user
    tasks = []
    
    # Only show tasks for workers/accountants
    if user.role in ['worker', 'accountant'] and hasattr(user, 'employee'):
        tasks = WorkRecord.objects.filter(
            employee=user.employee
        ).select_related(
            'product', 'task', 'product_task'
        ).order_by('-created_at')[:5]
    
    return render(request, 'dashboard/_recent_tasks.html', {
        'tasks': tasks,
    })


@login_required
def statistics(request):
    """
    Statistics page with charts and detailed analytics for workers.
    Admin users are redirected to admin panel.
    """
    user = request.user
    
    # Redirect admin users to admin panel
    if user.role in [User.Role.SUPER_ADMIN, User.Role.TENANT_ADMIN]:
        return redirect('admin_panel:dashboard')
    
    # Redirect masters to master panel
    if user.role == User.Role.MASTER:
        return redirect('master:dashboard')
    
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)
    
    # Default stats
    stats = {
        'daily': {'tasks': 0, 'earnings': 0},
        'weekly': {'tasks': 0, 'earnings': 0},
        'monthly': {'tasks': 0, 'earnings': 0},
        'chart_data': {'labels': [], 'data': []},
    }
    
    # Get real data if user has employee record
    if hasattr(user, 'employee'):
        employee = user.employee
        
        # Daily stats
        daily_records = WorkRecord.objects.filter(
            employee=employee,
            work_date=today
        )
        stats['daily'] = {
            'tasks': daily_records.count(),
            'earnings': daily_records.aggregate(Sum('total_payment'))['total_payment__sum'] or 0,
        }
        
        # Weekly stats
        weekly_records = WorkRecord.objects.filter(
            employee=employee,
            work_date__gte=week_start,
            work_date__lte=today
        )
        stats['weekly'] = {
            'tasks': weekly_records.count(),
            'earnings': weekly_records.aggregate(Sum('total_payment'))['total_payment__sum'] or 0,
        }
        
        # Monthly stats
        monthly_records = WorkRecord.objects.filter(
            employee=employee,
            work_date__year=today.year,
            work_date__month=today.month
        )
        stats['monthly'] = {
            'tasks': monthly_records.count(),
            'earnings': monthly_records.aggregate(Sum('total_payment'))['total_payment__sum'] or 0,
        }
        
        # Chart data - last 7 days
        chart_labels = []
        chart_data = []
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            chart_labels.append(day.strftime('%d.%m'))
            
            day_count = WorkRecord.objects.filter(
                employee=employee,
                work_date=day
            ).aggregate(Sum('quantity'))['quantity__sum'] or 0
            
            chart_data.append(day_count)
        
        stats['chart_data'] = {
            'labels': json.dumps(chart_labels),
            'data': json.dumps(chart_data),
        }
    
    return render(request, 'statistics.html', {
        'stats': stats,
    })


@login_required
def profile(request):
    """
    User profile page with settings.
    Available for all user roles.
    """
    return render(request, 'profile.html', {
        'user': request.user,
    })


# TV Dashboard Views (for big screen analytics)

def tv_dashboard(request):
    """
    Full-screen dashboard for TV displays.
    Auto-refreshes every 30 seconds via HTMX.
    Shows company-wide statistics (all employees).
    """
    today = date.today()
    
    # Get current time for display
    from datetime import datetime
    now = datetime.now()
    current_time = now.strftime('%H:%M:%S')
    current_date = now.strftime('%d.%m.%Y, %A')
    
    # Company-wide statistics for today (current tenant only)
    today_records = WorkRecord.objects.filter(
        tenant=request.tenant,
        work_date=today
    )
    
    stats = {
        'total_production': today_records.aggregate(
            Sum('quantity')
        )['quantity__sum'] or 0,
        'active_workers': today_records.values('employee').distinct().count(),
        'completed_tasks': today_records.filter(
            status__in=[WorkRecord.Status.COMPLETED, WorkRecord.Status.APPROVED]
        ).count(),
        'total_payment': today_records.aggregate(
            Sum('total_payment')
        )['total_payment__sum'] or 0,
    }
    
    # Chart data - hourly production for today
    chart_labels = []
    chart_data = []
    
    # Get hourly data (8:00 to current hour)
    current_hour = now.hour
    start_hour = 8  # Work starts at 8:00
    
    for hour in range(start_hour, min(current_hour + 1, 19)):  # Until 18:00
        chart_labels.append(f'{hour:02d}:00')
        
        # Get production for this hour (current tenant only)
        hour_production = WorkRecord.objects.filter(
            tenant=request.tenant,
            work_date=today,
            created_at__hour=hour
        ).aggregate(Sum('quantity'))['quantity__sum'] or 0
        
        chart_data.append(hour_production)
    
    return render(request, 'dashboard/tv.html', {
        'stats': stats,
        'chart_data': {
            'labels': json.dumps(chart_labels),
            'data': json.dumps(chart_data),
        },
        'current_time': current_time,
        'current_date': current_date,
    })


def tv_kpi_stats(request):
    """
    HTMX partial for KPI cards on TV dashboard.
    Auto-refreshes to show real-time data.
    """
    today = date.today()
    
    # Company-wide statistics (current tenant only)
    today_records = WorkRecord.objects.filter(
        tenant=request.tenant,
        work_date=today
    )
    
    stats = {
        'total_production': today_records.aggregate(
            Sum('quantity')
        )['quantity__sum'] or 0,
        'active_workers': today_records.values('employee').distinct().count(),
        'completed_tasks': today_records.filter(
            status__in=[WorkRecord.Status.COMPLETED, WorkRecord.Status.APPROVED]
        ).count(),
        'total_payment': today_records.aggregate(
            Sum('total_payment')
        )['total_payment__sum'] or 0,
    }
    
    return render(request, 'dashboard/_tv_kpi_cards.html', stats)


def tv_top_performers(request):
    """
    HTMX partial for top performers list.
    Shows top 10 employees by production today.
    """
    today = date.today()
    
    # Get top performers for today (current tenant only)
    top_performers = WorkRecord.objects.filter(
        tenant=request.tenant,
        work_date=today
    ).values(
        'employee__full_name'
    ).annotate(
        total_quantity=Sum('quantity'),
        total_payment=Sum('total_payment')
    ).order_by('-total_quantity')[:10]
    
    return render(request, 'dashboard/_tv_top_performers.html', {
        'performers': top_performers,
    })

