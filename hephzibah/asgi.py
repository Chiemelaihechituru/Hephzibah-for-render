"""
ASGI config for the hephzibah project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hephzibah.settings')

application = get_asgi_application()
