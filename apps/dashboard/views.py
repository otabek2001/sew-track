"""
Dashboard views with mobile-first design.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import date, timedelta
import json

from apps.tasks.models import Task, WorkRecord
from apps.employees.models import Employee


@login_required
def dashboard(request):
    """
    Main dashboard view for all user roles.
    Mobile-optimized with quick stats and recent activity.
    """
    user = request.user
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
    HTMX partial view for recent tasks.
    Returns only the HTML fragment for dynamic loading.
    """
    user = request.user
    tasks = []
    
    # Get recent work records
    if hasattr(user, 'employee'):
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
    Statistics page with charts and detailed analytics.
    """
    user = request.user
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
    """
    return render(request, 'profile.html', {
        'user': request.user,
    })


# TV Dashboard Views (for big screen analytics)

def tv_dashboard(request):
    """
    Full-screen dashboard for TV displays.
    Auto-refreshes every 30 seconds via HTMX.
    """
    today = date.today()
    
    # Mock data
    stats = {
        'total_production': 1234,
        'active_workers': 45,
        'completed_tasks': 892,
        'daily_plan_progress': 95,
    }
    
    # Chart data for production timeline
    chart_data = {
        'labels': ['8:00', '9:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00'],
        'data': [45, 78, 92, 120, 98, 145, 167, 189, 203],
    }
    
    return render(request, 'dashboard/tv.html', {
        'stats': stats,
        'chart_data': chart_data,
    })


def tv_kpi_stats(request):
    """
    HTMX partial for KPI cards on TV dashboard.
    Auto-refreshes to show real-time data.
    """
    today = date.today()
    
    stats = {
        'total_production': 1234,
        'active_workers': 45,
        'completed_tasks': 892,
        'daily_plan_progress': 95,
    }
    
    return render(request, 'dashboard/_tv_kpi_cards.html', stats)


def tv_top_performers(request):
    """
    HTMX partial for top performers list.
    """
    # Mock data
    top_performers = [
        {'name': 'Fatima Karimova', 'tasks': 45, 'earnings': 350000},
        {'name': 'Dilnoza Rashidova', 'tasks': 42, 'earnings': 335000},
        {'name': 'Nodira Saidova', 'tasks': 38, 'earnings': 298000},
        {'name': 'Malika Tursunova', 'tasks': 36, 'earnings': 285000},
        {'name': 'Zilola Alimova', 'tasks': 34, 'earnings': 272000},
    ]
    
    return render(request, 'dashboard/_tv_top_performers.html', {
        'performers': top_performers,
    })

