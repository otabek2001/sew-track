"""
Django production settings for SEW-TRACK project.

Settings for production environment.
"""

from .base import *  # noqa: F401, F403

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Security Settings
SECURE_SSL_REDIRECT = env('SECURE_SSL_REDIRECT', default=True)  # noqa: F405
SECURE_HSTS_SECONDS = env('SECURE_HSTS_SECONDS', default=31536000)  # noqa: F405
SECURE_HSTS_INCLUDE_SUBDOMAINS = env('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=True)  # noqa: F405
SECURE_HSTS_PRELOAD = env('SECURE_HSTS_PRELOAD', default=True)  # noqa: F405
SESSION_COOKIE_SECURE = env('SESSION_COOKIE_SECURE', default=True)  # noqa: F405
CSRF_COOKIE_SECURE = env('CSRF_COOKIE_SECURE', default=True)  # noqa: F405
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Static files (CSS, JavaScript, Images)
# Use WhiteNoise for serving static files in production
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')  # noqa: F405
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Database Connection Pooling
DATABASES['default']['CONN_MAX_AGE'] = env('DB_CONN_MAX_AGE', default=600)  # noqa: F405
DATABASES['default']['OPTIONS'] = {  # noqa: F405
    'connect_timeout': 10,
    'options': '-c statement_timeout=30000',
}

# Email Backend (Production)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST', default='localhost')  # noqa: F405
EMAIL_PORT = env('EMAIL_PORT', default=587)  # noqa: F405
EMAIL_USE_TLS = env('EMAIL_USE_TLS', default=True)  # noqa: F405
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')  # noqa: F405
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')  # noqa: F405
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='noreply@sewtrack.uz')  # noqa: F405

# Sentry for error tracking (Optional)
SENTRY_DSN = env('SENTRY_DSN', default=None)  # noqa: F405
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration
    
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(),
            CeleryIntegration(),
        ],
        traces_sample_rate=0.1,
        send_default_pii=False,
        environment='production',
    )

# Logging - Production level
LOGGING['loggers']['django']['level'] = 'WARNING'  # noqa: F405
LOGGING['root']['level'] = 'WARNING'  # noqa: F405

