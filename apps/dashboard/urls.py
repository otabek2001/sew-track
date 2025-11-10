"""
URL patterns for Dashboard app.
"""

from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Main dashboard
    path('', views.dashboard, name='dashboard'),
    
    # HTMX partials
    path('recent-tasks/', views.recent_tasks, name='recent-tasks'),
    
    # TV Dashboard
    path('tv/', views.tv_dashboard, name='tv'),
    path('tv/kpi-stats/', views.tv_kpi_stats, name='tv-kpi-stats'),
    path('tv/top-performers/', views.tv_top_performers, name='tv-top-performers'),
]

