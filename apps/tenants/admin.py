"""
Admin configuration for Tenants app.
"""

from django.contrib import admin
from .models import Tenant, TenantMembership


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'owner', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'slug', 'owner__username', 'owner__email']
    readonly_fields = ['slug', 'created_at', 'updated_at', 'activated_at']
    
    fieldsets = [
        ('Basic Information', {
            'fields': ['name', 'slug', 'owner', 'is_active']
        }),
        ('Contact Information', {
            'fields': ['address', 'phone', 'email']
        }),
        ('Settings', {
            'fields': ['settings', 'notes'],
            'classes': ['collapse']
        }),
        ('Timestamps', {
            'fields': ['activated_at', 'created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]


@admin.register(TenantMembership)
class TenantMembershipAdmin(admin.ModelAdmin):
    list_display = ['user', 'tenant', 'role', 'is_active', 'joined_at']
    list_filter = ['role', 'is_active', 'joined_at']
    search_fields = ['user__username', 'user__email', 'tenant__name']
    readonly_fields = ['joined_at', 'created_at', 'updated_at']
    
    fieldsets = [
        ('Membership', {
            'fields': ['tenant', 'user', 'role', 'is_active']
        }),
        ('Timestamps', {
            'fields': ['joined_at', 'created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]
