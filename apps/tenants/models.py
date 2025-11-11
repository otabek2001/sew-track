"""
Tenant models for multi-tenancy support.

Each tenant represents a separate workshop/factory.
Data isolation is enforced at the database level.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from core.models import TimeStampedModel
import uuid

User = get_user_model()


class Tenant(TimeStampedModel):
    """
    Tenant model - represents a workshop/factory.
    
    One owner can have multiple tenants (workshops).
    Each tenant has its own employees, products, tasks, etc.
    """
    
    name = models.CharField(
        max_length=200,
        verbose_name='Workshop Name',
        help_text='E.g., "Oltin Ipak", "Bahor Tikuvchilik"'
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name='Slug',
        help_text='URL-friendly identifier'
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='owned_tenants',
        verbose_name='Owner',
        help_text='Primary owner of this tenant'
    )
    
    # Contact Info
    address = models.TextField(
        blank=True,
        verbose_name='Address'
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Phone Number'
    )
    email = models.EmailField(
        blank=True,
        verbose_name='Email'
    )
    
    # Settings (JSON field for flexibility)
    settings = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Settings',
        help_text='Tenant-specific settings (work hours, currency, etc.)'
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        verbose_name='Active Status'
    )
    activated_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Activation Date'
    )
    
    # Metadata
    notes = models.TextField(
        blank=True,
        verbose_name='Internal Notes'
    )
    
    class Meta:
        db_table = 'tenants'
        verbose_name = 'Tenant'
        verbose_name_plural = 'Tenants'
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['owner']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Auto-generate slug if not provided."""
        if not self.slug:
            self.slug = slugify(self.name)
            # Ensure uniqueness
            original_slug = self.slug
            counter = 1
            while Tenant.objects.filter(slug=self.slug).exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1
        super().save(*args, **kwargs)
    
    def activate(self):
        """Activate tenant."""
        from django.utils import timezone
        self.is_active = True
        self.activated_at = timezone.now()
        self.save(update_fields=['is_active', 'activated_at', 'updated_at'])
    
    def deactivate(self):
        """Deactivate tenant."""
        self.is_active = False
        self.save(update_fields=['is_active', 'updated_at'])


class TenantMembership(TimeStampedModel):
    """
    Many-to-many relationship between Users and Tenants.
    
    Allows users to belong to multiple tenants with different roles.
    E.g., A user can be an admin in one tenant and a viewer in another.
    """
    
    class Role(models.TextChoices):
        OWNER = 'owner', 'Owner'
        ADMIN = 'admin', 'Admin'
        MASTER = 'master', 'Master'
        ACCOUNTANT = 'accountant', 'Accountant'
        VIEWER = 'viewer', 'Viewer'
    
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='memberships',
        verbose_name='Tenant'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tenant_memberships',
        verbose_name='User'
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.VIEWER,
        verbose_name='Role in Tenant'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Active Membership'
    )
    joined_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Joined At'
    )
    
    class Meta:
        db_table = 'tenant_memberships'
        verbose_name = 'Tenant Membership'
        verbose_name_plural = 'Tenant Memberships'
        ordering = ['-joined_at']
        unique_together = [['tenant', 'user']]
        indexes = [
            models.Index(fields=['tenant', 'user']),
            models.Index(fields=['user', 'is_active']),
        ]
    
    def __str__(self):
        return f'{self.user.username} @ {self.tenant.name} ({self.get_role_display()})'
