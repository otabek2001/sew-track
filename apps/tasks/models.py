"""
Task models for SEW-TRACK.

Tasks represent operations that can be performed on products.
"""

from django.db import models
from core.models import TimeStampedModel


class Task(TimeStampedModel):
    """
    Task (Operation) model.
    
    Represents an operation that can be performed on a product
    (e.g., "Олди релф лента ёпиштириш").
    """
    
    class Category(models.TextChoices):
        CUTTING = 'cutting', 'Cutting'
        SEWING = 'sewing', 'Sewing'
        IRONING = 'ironing', 'Ironing'
        PACKAGING = 'packaging', 'Packaging'
        QUALITY_CHECK = 'quality_check', 'Quality Check'
        OTHER = 'other', 'Other'
    
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name='Tenant',
        help_text='Workshop this task belongs to'
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Task Code',
        help_text='Unique task identifier (e.g., TASK-001)'
    )
    name_uz = models.CharField(
        max_length=200,
        verbose_name='Name (Uzbek)'
    )
    name_ru = models.CharField(
        max_length=200,
        verbose_name='Name (Russian)'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Description'
    )
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.SEWING,
        verbose_name='Category'
    )
    sequence_order = models.IntegerField(
        default=0,
        verbose_name='Sequence Order',
        help_text='Order in which this task is typically performed'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Active Status'
    )
    
    class Meta:
        db_table = 'tasks'
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'
        ordering = ['sequence_order', 'code']
        indexes = [
            models.Index(fields=['tenant']),
            models.Index(fields=['code']),
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
            models.Index(fields=['tenant', 'is_active']),
        ]
    
    def __str__(self):
        return f'{self.code} - {self.name_uz}'
    
    def get_name(self, language='uz'):
        """Get task name in specified language."""
        return self.name_uz if language == 'uz' else self.name_ru


class WorkRecord(TimeStampedModel):
    """
    WorkRecord model - daily work records from employees.
    
    Represents work completed by an employee on a specific product/task.
    """
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        COMPLETED = 'completed', 'Completed'
        REJECTED = 'rejected', 'Rejected'
        APPROVED = 'approved', 'Approved'
    
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        related_name='work_records',
        verbose_name='Tenant',
        help_text='Workshop this work record belongs to'
    )
    employee = models.ForeignKey(
        'employees.Employee',
        on_delete=models.CASCADE,
        related_name='work_records',
        verbose_name='Employee'
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='work_records',
        verbose_name='Product'
    )
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='work_records',
        verbose_name='Task'
    )
    product_task = models.ForeignKey(
        'products.ProductTask',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='work_records',
        verbose_name='Product Task Link',
        help_text='Link to ProductTask for price lookup'
    )
    quantity = models.PositiveIntegerField(
        verbose_name='Quantity',
        help_text='Number of units completed'
    )
    price_per_unit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Price Per Unit',
        help_text='Price per unit in UZS'
    )
    total_payment = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Total Payment',
        help_text='Calculated: quantity * price_per_unit'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='Status'
    )
    work_date = models.DateField(
        verbose_name='Work Date',
        help_text='Date when work was performed'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='Notes'
    )
    approved_by = models.ForeignKey(
        'employees.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_work_records',
        verbose_name='Approved By'
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Approved At'
    )
    
    class Meta:
        db_table = 'work_records'
        verbose_name = 'Work Record'
        verbose_name_plural = 'Work Records'
        ordering = ['-work_date', '-created_at']
        indexes = [
            models.Index(fields=['tenant']),
            models.Index(fields=['employee', 'work_date']),
            models.Index(fields=['status']),
            models.Index(fields=['work_date']),
            models.Index(fields=['product', 'task']),
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['tenant', 'work_date']),
        ]
    
    def __str__(self):
        return f'{self.employee.full_name} - {self.product.article_code} - {self.task.code} ({self.quantity})'
    
    def save(self, *args, **kwargs):
        """Calculate total payment before saving."""
        if not self.total_payment or self.total_payment == 0:
            self.total_payment = self.quantity * self.price_per_unit
        super().save(*args, **kwargs)
    
    def approve(self, approved_by):
        """Approve this work record."""
        from django.utils import timezone
        
        self.status = self.Status.APPROVED
        self.approved_by = approved_by
        self.approved_at = timezone.now()
        self.save(update_fields=['status', 'approved_by', 'approved_at', 'updated_at'])
    
    def reject(self):
        """Reject this work record."""
        self.status = self.Status.REJECTED
        self.save(update_fields=['status', 'notes', 'updated_at'])
    
    def complete(self):
        """Mark as completed."""
        self.status = self.Status.COMPLETED
        self.save(update_fields=['status', 'updated_at'])
    
    def reset_to_pending(self, reason=''):
        """
        Reset status to pending (for tenant admin to correct master's mistakes).
        
        This allows tenant admin to reset approved or rejected records back to pending
        status if master made a mistake. The approval history (approved_by, approved_at)
        is preserved for audit purposes.
        
        Args:
            reason: Optional reason for resetting (will be added to notes)
        """
        from django.utils import timezone
        
        old_status = self.status
        self.status = self.Status.PENDING
        
        # Add reason to notes if provided
        if reason:
            reset_note = f"\n\n[Status qaytarildi: {old_status} -> pending, {timezone.now().strftime('%d.%m.%Y %H:%M')}]"
            if self.approved_by:
                reset_note += f" (Tasdiqlagan: {self.approved_by.full_name})"
            reset_note += f"\nSabab: {reason}"
            self.notes = (self.notes or '') + reset_note
        
        self.save(update_fields=['status', 'notes', 'updated_at'])