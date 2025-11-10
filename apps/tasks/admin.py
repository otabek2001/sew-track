"""
Django admin configuration for Tasks app.
"""

from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Admin interface for Task model."""
    
    list_display = [
        'code', 'name_uz', 'name_ru', 'category',
        'sequence_order', 'is_active', 'created_at'
    ]
    list_filter = ['category', 'is_active']
    search_fields = ['code', 'name_uz', 'name_ru']
    ordering = ['sequence_order', 'code']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'name_uz', 'name_ru', 'description')
        }),
        ('Classification', {
            'fields': ('category', 'sequence_order', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
