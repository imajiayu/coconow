from channels.routing import ProtocolTypeRouter,URLRouter
from websocket_service.urls import websocket_url

application = ProtocolTypeRouter({
    "websocket":URLRouter(
        websocket_url
    )
})