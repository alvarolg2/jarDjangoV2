"""
WSGI config for jar_backend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import logging
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jar_backend.settings')

application = get_wsgi_application()

from jar_backend import __version__
logger = logging.getLogger('jar_backend')
logger.info(f"JAR Backend v{__version__} iniciado correctamente")

