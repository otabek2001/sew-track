"""
Django settings module.

Import settings based on DJANGO_SETTINGS_MODULE environment variable.
"""

import os

# Default to development settings if not specified
SETTINGS_MODULE = os.environ.get('DJANGO_SETTINGS_MODULE', 'config.settings.development')

if 'development' in SETTINGS_MODULE:
    from .development import *  # noqa: F401, F403
elif 'production' in SETTINGS_MODULE:
    from .production import *  # noqa: F401, F403
elif 'test' in SETTINGS_MODULE:
    from .test import *  # noqa: F401, F403
else:
    from .base import *  # noqa: F401, F403

