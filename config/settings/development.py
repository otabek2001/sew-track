"""
Django development settings for SEW-TRACK project.

Settings for local development environment.
"""

from .base import *  # noqa: F401, F403

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]', '192.168.0.113', '192.168.0.*']

# Development apps
INSTALLED_APPS += [  # noqa: F405
    'debug_toolbar',
    'django_extensions',
]

# Debug Toolbar
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']  # noqa: F405

INTERNAL_IPS = [
    '127.0.0.1',
    '192.168.0.113',
]

# Django Debug Toolbar Settings
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,  # noqa: F405
}

# REST Framework - Add Browsable API in development
REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = [  # noqa: F405
    'rest_framework.renderers.JSONRenderer',
    'rest_framework.renderers.BrowsableAPIRenderer',
]

# Email Backend (Console for development)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# CORS - Allow all origins in development
CORS_ALLOW_ALL_ORIGINS = True

# Celery - Eager execution for development
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Logging - More verbose in development
LOGGING['loggers']['django']['level'] = 'DEBUG'  # noqa: F405
LOGGING['root']['level'] = 'DEBUG'  # noqa: F405

