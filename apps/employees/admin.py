"""
Django admin configuration for Employees app.
"""

from django.contrib import admin
from .models import Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """Admin interface for Employee model."""
    
    list_display = [
        'full_name', 'user', 'position', 'employment_type',
        'is_active', 'hired_at', 'created_at'
    ]
    list_filter = ['position', 'employment_type', 'is_active', 'hired_at']
    search_fields = ['full_name', 'phone', 'user__email']
    ordering = ['-created_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'full_name', 'phone')
        }),
        ('Employment Details', {
            'fields': ('position', 'employment_type', 'hourly_rate', 'hired_at', 'terminated_at')
        }),
        ('Status', {
            'fields': ('is_active', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related('user')
