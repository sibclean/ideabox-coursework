from django.urls import re_path
from . import consumers

# Здесь мы прописываем URL, по которому браузер будет подключаться к сокету
websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<conversation_id>\w+)/$', consumers.ChatConsumer.as_asgi()),
]

