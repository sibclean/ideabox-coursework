import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ideas.settings')
django_asgi_app = get_asgi_application()

# Импортируем наши маршруты
import ideas.routing

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            ideas.routing.websocket_urlpatterns # Подключаем сюда
        )
    ),
})