"""
Dashboard views with mobile-first design.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import date, timedelta

# Placeholder imports - will be implemented when models are ready
# from apps.tasks.models import Task, WorkRecord
# from apps.employees.models import Employee


@login_required
def dashboard(request):
    """
    Main dashboard view for all user roles.
    Mobile-optimized with quick stats and recent activity.
    """
    user = request.user
    today = date.today()
    
    # Mock data for now - replace with actual queries
    stats = {
        'today_tasks': 12,
        'completed': 8,
        'in_progress': 4,
        'earnings': 85000,
    }
    
    # TODO: Implement actual queries when models are ready
    # if hasattr(user, 'employee'):
    #     stats = {
    #         'today_tasks': WorkRecord.objects.filter(
    #             employee=user.employee,
    #             date=today
    #         ).count(),
    #         'completed': WorkRecord.objects.filter(
    #             employee=user.employee,
    #             date=today,
    #             status='completed'
    #         ).count(),
    #         'in_progress': WorkRecord.objects.filter(
    #             employee=user.employee,
    #             date=today,
    #             status='in_progress'
    #         ).count(),
    #         'earnings': WorkRecord.objects.filter(
    #             employee=user.employee,
    #             date=today,
    #             status='completed'
    #         ).aggregate(total=Sum('payment_amount'))['total'] or 0,
    #     }
    
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
    
    # Mock data - replace with actual query
    tasks = []
    
    # TODO: Implement when models are ready
    # if hasattr(user, 'employee'):
    #     tasks = WorkRecord.objects.filter(
    #         employee=user.employee
    #     ).select_related(
    #         'product', 'operation'
    #     ).order_by('-created_at')[:5]
    
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
    
    # Mock data
    stats = {
        'daily': {
            'tasks': 12,
            'earnings': 85000,
        },
        'weekly': {
            'tasks': 67,
            'earnings': 523000,
        },
        'monthly': {
            'tasks': 234,
            'earnings': 1850000,
        },
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

