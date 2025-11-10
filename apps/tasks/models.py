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
            models.Index(fields=['code']),
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f'{self.code} - {self.name_uz}'
    
    def get_name(self, language='uz'):
        """Get task name in specified language."""
        return self.name_uz if language == 'uz' else self.name_ru
