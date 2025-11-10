"""
Master app configuration.
For Master/Admin approval workflow.
"""

from django.apps import AppConfig


class MasterConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.master'
    verbose_name = 'Master Panel'

