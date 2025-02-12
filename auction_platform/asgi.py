import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auction_platform.settings')
django.setup()  # Ensure Django is fully set up before further imports

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

# Now import the routing modules that rely on Django apps being loaded:
from auctions.routing import websocket_urlpatterns
import messaging.routing

# Initialize the Django ASGI application
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns + messaging.routing.websocket_urlpatterns
        )
    ),
})
