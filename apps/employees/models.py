"""
Employee models for SEW-TRACK.
"""

from django.db import models
from django.contrib.auth import get_user_model
from core.models import TimeStampedModel
from core.validators import validate_phone_number

User = get_user_model()


class Employee(TimeStampedModel):
    """
    Employee model - represents factory workers.
    
    Each employee is linked to a User account.
    """
    
    class EmploymentType(models.TextChoices):
        FULL_TIME = 'full_time', 'Full Time'
        PART_TIME = 'part_time', 'Part Time'
        CONTRACT = 'contract', 'Contract'
        TEMPORARY = 'temporary', 'Temporary'
    
    class Position(models.TextChoices):
        WORKER = 'worker', 'Worker'
        MASTER = 'master', 'Master'
        QUALITY_CONTROLLER = 'quality_controller', 'Quality Controller'
        SUPERVISOR = 'supervisor', 'Supervisor'
    
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        related_name='employees',
        verbose_name='Tenant',
        help_text='Workshop this employee belongs to'
    )
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='employee',
        verbose_name='User Account'
    )
    full_name = models.CharField(
        max_length=200,
        verbose_name='Full Name'
    )
    phone = models.CharField(
        max_length=20,
        validators=[validate_phone_number],
        verbose_name='Phone Number'
    )
    position = models.CharField(
        max_length=50,
        choices=Position.choices,
        default=Position.WORKER,
        verbose_name='Position'
    )
    employment_type = models.CharField(
        max_length=20,
        choices=EmploymentType.choices,
        default=EmploymentType.FULL_TIME,
        verbose_name='Employment Type'
    )
    hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Hourly Rate',
        help_text='Base hourly rate in UZS'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Active Status'
    )
    hired_at = models.DateField(
        verbose_name='Hire Date'
    )
    terminated_at = models.DateField(
        null=True,
        blank=True,
        verbose_name='Termination Date'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='Notes'
    )
    
    class Meta:
        db_table = 'employees'
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant']),
            models.Index(fields=['user']),
            models.Index(fields=['position']),
            models.Index(fields=['is_active']),
            models.Index(fields=['tenant', 'is_active']),
        ]
    
    def __str__(self):
        return f'{self.full_name} ({self.get_position_display()})'
    
    def activate(self):
        """Activate employee."""
        self.is_active = True
        self.terminated_at = None
        self.save(update_fields=['is_active', 'terminated_at', 'updated_at'])
    
    def deactivate(self, termination_date=None):
        """Deactivate employee."""
        from datetime import date
        
        self.is_active = False
        self.terminated_at = termination_date or date.today()
        self.save(update_fields=['is_active', 'terminated_at', 'updated_at'])
