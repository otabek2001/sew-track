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


def home_redirect(request):
    """Redirect to dashboard if authenticated, else to login."""
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')
    return redirect('login')


urlpatterns = [
    # Home - redirect to dashboard or login
    path('', home_redirect, name='home'),
    
    # Authentication
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    # Dashboard (Web UI)
    path('dashboard/', include('apps.dashboard.urls')),
    
    # Additional pages (imported from dashboard views)
    path('statistics/', views.statistics, name='statistics'),
    path('profile/', views.profile, name='profile'),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API v1
    path('api/v1/accounts/', include('apps.accounts.urls')),
    path('api/v1/employees/', include('apps.employees.urls')),
    path('api/v1/', include('apps.products.urls')),
    path('api/v1/tasks/', include('apps.tasks.urls')),
]

# Debug Toolbar (only in development)
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]

# Static and Media files (only in development)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
