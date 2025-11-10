"""
User and Authentication models for SEW-TRACK.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from core.models import TimeStampedModel


class User(AbstractUser, TimeStampedModel):
    """
    Custom User model with additional fields.
    
    Roles:
    - super_admin: Full system access
    - tenant_admin: Workshop administrator
    - master: Shift supervisor
    - worker: Factory worker
    - accountant: Accountant
    - viewer: Read-only access
    """
    
    class Role(models.TextChoices):
        SUPER_ADMIN = 'super_admin', 'Super Admin'
        TENANT_ADMIN = 'tenant_admin', 'Tenant Admin'
        MASTER = 'master', 'Master'
        WORKER = 'worker', 'Worker'
        ACCOUNTANT = 'accountant', 'Accountant'
        VIEWER = 'viewer', 'Viewer'
    
    email = models.EmailField(
        verbose_name='Email address',
        null=True,
        blank=True
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Phone number'
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.WORKER,
        verbose_name='User role'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Active status'
    )
    
    # Remove username requirement, use username instead
    USERNAME_FIELD = 'username'    
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.email} ({self.get_role_display()})'
    
    @property
    def is_admin(self):
        """Check if user is admin."""
        return self.role in [self.Role.SUPER_ADMIN, self.Role.TENANT_ADMIN]
    
    @property
    def is_master_or_above(self):
        """Check if user is master or higher."""
        return self.role in [
            self.Role.SUPER_ADMIN,
            self.Role.TENANT_ADMIN,
            self.Role.MASTER
        ]
