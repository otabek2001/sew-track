"""
Django admin configuration for Products app.
"""

from django.contrib import admin
from .models import Product, ProductTask


class ProductTaskInline(admin.TabularInline):
    """Inline admin for ProductTask."""
    model = ProductTask
    extra = 1
    fields = ['task', 'base_price', 'premium_price', 'estimated_minutes']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin interface for Product model."""
    
    list_display = [
        'article_code', 'name', 'category',
        'is_active', 'created_at'
    ]
    list_filter = ['category', 'is_active']
    search_fields = ['article_code', 'name']
    ordering = ['article_code']
    inlines = [ProductTaskInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('article_code', 'name', 'category', 'description')
        }),
        ('Status & Metadata', {
            'fields': ('is_active', 'metadata')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ProductTask)
class ProductTaskAdmin(admin.ModelAdmin):
    """Admin interface for ProductTask model."""
    
    list_display = [
        'product', 'task', 'base_price', 'premium_price',
        'estimated_minutes', 'created_at'
    ]
    list_filter = ['price_type']
    search_fields = ['product__article_code', 'task__code']
    ordering = ['product', 'task']
    
    fieldsets = (
        ('Relationship', {
            'fields': ('product', 'task')
        }),
        ('Pricing', {
            'fields': ('base_price', 'premium_price', 'price_type')
        }),
        ('Additional Info', {
            'fields': ('estimated_minutes', 'metadata')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related('product', 'task')
