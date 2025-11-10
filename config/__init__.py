"""
Django project initialization.
"""

# Import Celery app to ensure it's loaded when Django starts
from celery_app import celery_app

__all__ = ('celery_app',)

