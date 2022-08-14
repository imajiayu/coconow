from django.urls import path
from websocket_service.WebSSH import WebSSHService
from websocket_service.CoProgramming import CoProgrammingConsumer
from websocket_service.ChatRoom import ChatRoomConsumer
websocket_url = [
    path("editor/",CoProgrammingConsumer.as_asgi()),
    path("web/",WebSSHService.as_asgi()),
    path("chat/",ChatRoomConsumer.as_asgi()),
]