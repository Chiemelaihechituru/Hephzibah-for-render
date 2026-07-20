"""
WSGI config for the hephzibah project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hephzibah.settings')

application = get_wsgi_application()
