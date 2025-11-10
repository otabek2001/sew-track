"""
Core models for SEW-TRACK project.

Base models that will be inherited by other apps.
"""

import uuid
from django.db import models


class TimeStampedModel(models.Model):
    """
    Abstract base model with UUID primary key and timestamp fields.
    
    All models in the project should inherit from this model.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='ID'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created at'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Updated at'
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def __str__(self):
        return str(self.id)

