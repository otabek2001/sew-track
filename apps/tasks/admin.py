"""
Django admin configuration for Tasks app.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Task, WorkRecord


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


@admin.register(WorkRecord)
class WorkRecordAdmin(admin.ModelAdmin):
    """Admin interface for WorkRecord model."""
    
    list_display = [
        'id', 'employee_name', 'product_display', 'task_display',
        'quantity', 'total_payment', 'status_badge', 'work_date', 'created_at'
    ]
    list_filter = ['status', 'work_date', 'product', 'task']
    search_fields = [
        'employee__full_name', 'employee__user__username',
        'product__article_code', 'product__name',
        'task__code', 'task__name_uz'
    ]
    ordering = ['-work_date', '-created_at']
    date_hierarchy = 'work_date'
    
    fieldsets = (
        ('Work Information', {
            'fields': ('employee', 'product', 'task', 'product_task', 'work_date')
        }),
        ('Quantity & Payment', {
            'fields': ('quantity', 'price_per_unit', 'total_payment')
        }),
        ('Status', {
            'fields': ('status', 'notes')
        }),
        ('Approval', {
            'fields': ('approved_by', 'approved_at'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'total_payment']
    
    autocomplete_fields = ['employee', 'product', 'task', 'product_task', 'approved_by']
    
    def employee_name(self, obj):
        """Display employee name with link."""
        return obj.employee.full_name
    employee_name.short_description = 'Employee'
    employee_name.admin_order_field = 'employee__full_name'
    
    def product_display(self, obj):
        """Display product with article code."""
        return f'{obj.product.article_code} - {obj.product.name}'
    product_display.short_description = 'Product'
    product_display.admin_order_field = 'product__article_code'
    
    def task_display(self, obj):
        """Display task with code."""
        return f'{obj.task.code} - {obj.task.name_uz}'
    task_display.short_description = 'Task'
    task_display.admin_order_field = 'task__code'
    
    def status_badge(self, obj):
        """Display status with color badge."""
        colors = {
            'pending': '#FFA500',
            'completed': '#28A745',
            'approved': '#007BFF',
            'rejected': '#DC3545',
        }
        color = colors.get(obj.status, '#6C757D')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    actions = ['approve_records', 'reject_records']
    
    def approve_records(self, request, queryset):
        """Bulk approve work records."""
        count = 0
        for record in queryset.filter(status=WorkRecord.Status.PENDING):
            # Use request.user's employee if exists
            approved_by = getattr(request.user, 'employee', None)
            if approved_by:
                record.approve(approved_by)
                count += 1
        
        self.message_user(request, f'{count} work records approved.')
    approve_records.short_description = 'Approve selected work records'
    
    def reject_records(self, request, queryset):
        """Bulk reject work records."""
        count = queryset.filter(status=WorkRecord.Status.PENDING).update(
            status=WorkRecord.Status.REJECTED
        )
        self.message_user(request, f'{count} work records rejected.')
    reject_records.short_description = 'Reject selected work records'
