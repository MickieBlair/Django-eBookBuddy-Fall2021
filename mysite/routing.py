from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import path, re_path
from django.core.asgi import get_asgi_application

from jitsi_data.consumer_jitsi import JitsiConsumer

from websockets._status_consumer import StatusConsumer

from websockets.consumer_match import MatchConsumer
from websockets.consumer_room_chat import PublicChatConsumer
from websockets.consumer_staff_chat import StaffChatConsumer
from websockets.consumer_private_chat import ChatConsumer
from websockets.consumer_echo import EchoConsumer



application = ProtocolTypeRouter({
	"http": get_asgi_application(),
	'websocket': AllowedHostsOriginValidator(
		AuthMiddlewareStack(
			URLRouter([
					path('jitsi_data/', JitsiConsumer.as_asgi()),
					path('status/', StatusConsumer.as_asgi()),
					path('match/<location_id>/', MatchConsumer.as_asgi()),
					path('jitsi_chat/<room_id>/', PublicChatConsumer.as_asgi()),
					path('staff_chat/<room_id>/', StaffChatConsumer.as_asgi()),
					path('private_chat/<room_id>/', ChatConsumer.as_asgi()),
					path('echo/', EchoConsumer.as_asgi()),
					
			])
		)
	),
})


