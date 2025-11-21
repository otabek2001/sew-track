"""
URL configuration for SEW-TRACK project.
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from apps.dashboard import views
from apps.accounts.web_views import CustomLoginView, CustomLogoutView


def home_redirect(request):
    """Redirect to appropriate dashboard based on user role."""
    if not request.user.is_authenticated:
        return redirect('login')
    
    user = request.user
    
    # Owner/Tenant Admin → Admin Panel
    if user.role in [user.Role.SUPER_ADMIN, user.Role.TENANT_ADMIN]:
        return redirect('admin_panel:dashboard')
    
    # Master → Master Panel
    if user.role == user.Role.MASTER:
        return redirect('master:dashboard')
    
    # Regular worker
    return redirect('dashboard:dashboard')


urlpatterns = [
    # Home - redirect to dashboard or login
    path('', home_redirect, name='home'),
    
    # Authentication
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(next_page='login'), name='logout'),
    
    # Dashboard (Web UI)
    path('dashboard/', include('apps.dashboard.urls', namespace='dashboard')),
    
    # Admin Panel (Owner/Tenant Admin)
    path('admin-panel/', include('apps.admin_panel.urls', namespace='admin_panel')),
    
    # Master Panel
    path('master/', include('apps.master.urls', namespace='master')),
    
    # Tasks & Work Records (Web UI)
    path('tasks/', include('apps.tasks.urls', namespace='tasks')),
    
    # Additional pages (imported from dashboard views)
    path('statistics/', views.statistics, name='statistics'),
    path('profile/', views.profile, name='profile'),
    
    # Test pages for debugging
    path('test/', lambda request: __import__('django.shortcuts').shortcuts.render(request, 'test.html'), name='test'),
    path('master/test/', lambda request: __import__('django.shortcuts').shortcuts.render(request, 'master/test_page.html'), name='master_test'),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API v1
    path('api/v1/accounts/', include('apps.accounts.urls')),
    path('api/v1/employees/', include('apps.employees.urls')),
    path('api/v1/tasks/', include('apps.tasks.urls')),
    path('api/v1/', include('apps.products.urls')),
    
    # Legacy API endpoints (for backward compatibility)
    path('api/', include('apps.tasks.urls')),
]

# Debug Toolbar (only in development)
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]

# Static and Media files
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # In production, static files are served by WhiteNoise middleware
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
