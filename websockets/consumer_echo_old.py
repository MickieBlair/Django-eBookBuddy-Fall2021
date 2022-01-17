from channels.consumer import AsyncConsumer
from channels.exceptions import StopConsumer

class EchoConsumer(AsyncConsumer):

    async def websocket_connect(self, event):
        print("Echo", str(self.scope["user"]))
        await self.send({
            "type": "websocket.accept",
            "message":str(self.scope["user"]) + " - Successfully Connected"
        })

        await self.send({
            "type": "connected_success",
            "message":str(self.scope["user"]) + " - Successfully Connected"
        })

    async def websocket_receive(self, event):
        await self.send({
            "type": "websocket.send",
            "text": event["text"],
        })

    async def connected_success(self, event):
        print("Sending THis", str(self.scope["user"]))
        await self.send({
            "type": "connected_success",
            "message": event["message"],
        })

    async def websocket_disconnect(self, message):
        """
        Called when a WebSocket connection is closed. Base level so you don't
        need to call super() all the time.
        """
     

        await self.disconnect(message["code"])
        raise StopConsumer()


    async def disconnect(self, code):
        """
        Called when a WebSocket connection is closed.
        """
        pass