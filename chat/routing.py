from django.urls import re_path
from . import consumer

websocket_urlpatterns = [
    re_path(r'^ws/chat/(?P<room_name>\w+)/$', consumer.ChatConsumer.as_asgi()),
    re_path(r'^ws/$', consumer.VideoChat.as_asgi()),
    re_path(r'^ws/notifications/$', consumer.NotificationConsumer.as_asgi()),
]
