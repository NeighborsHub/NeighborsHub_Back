"""
ASGI config for NeighborsHub project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NeighborsHub.settings')
django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

from NeighborsHub.middleware import TokenAuthMiddlewareChannels
from chat.routing import websocket_urlpatterns

# application = get_asgi_application()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": TokenAuthMiddlewareChannels(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
