import json
import asyncio
from channels.db import database_sync_to_async

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.auth import get_user
from asgiref.sync import async_to_sync
from django.utils import timezone

from channels.exceptions import StopConsumer

from users.models import CustomUser

class EchoConsumer(AsyncJsonWebsocketConsumer):
	async def connect(self):
		print("\n\n\n EchoConsumer: connect: " + str(self.scope["user"]))
		self.socket_group_name = 'echo'
		await self.channel_layer.group_add(
			self.socket_group_name,
			self.channel_name,		
		)

		await self.accept()



	async def websocket_disconnect(self, message):
		"""
		Called when a WebSocket connection is closed. Base level so you don't
		need to call super() all the time.
		"""
		print("\n*******************Echo Consumer: disconnect", timezone.now())

		try:
			print("Disconnecting Echo", str(self.scope["user"]))
			await self.leave_meeting_room()
		
		except Exception as e:
			print(e)

		try:
			for group in self.groups:
				await self.channel_layer.group_discard(group, self.channel_name)
		except AttributeError:
			raise InvalidChannelLayerError(
				"BACKEND is unconfigured or doesn't support groups"
				)

		await self.disconnect(message["code"])
		raise StopConsumer()

	async def disconnect(self, code):
		"""
		Called when a WebSocket connection is closed.
		"""
		pass


	async def receive_json(self, content):
		command = content.get("command", None)
		print("\n***** EchoConsumer: receive_json: " + str(self.scope["user"]))
		print("This is the content", content)
		self.card_title = content['page_header']
		member_id = content['member_id']

		if command =="join":

			await self.join_meeting_room(member_id)
			print("\n\n\nJOIN", content)
			# await self.channel_layer.group_send(
			# 	self.socket_group_name,
			# 	{
			# 		'type': 'member_joining',
			# 		# "full_name": self.scope["user"].full_name,
			# 		"username": self.scope["user"].username,
			# 		# "member_id": self.scope["user"].id,
			# 		# "role": self.role,
			# 		# "room_id": self.room.id,
			# 		# "room_name": self.room.name,
			# 		# "room_slug": self.room.slug,
			# 		# "room_row": "room_" + str(self.room.id),
			# 		# "room_count": self.room.num_participants,
			# 	}
			# )


	async def join_meeting_room(self, member_id):
		self.user = await get_user(self.scope)
		self.user_db = await get_user_db(member_id)
		print("Self.user", self.user)


		await self.channel_layer.group_send(
			self.socket_group_name,
			{
				'type': 'member_joining',
				# "full_name": self.scope["user"].full_name,
				"db_username": self.user_db.username,
				"scope_username": self.scope["user"].username,
				"username": self.user.username,
				"card_title": self.card_title,
				# "member_id": self.scope["user"].id,
				# "role": self.role,
				# "room_id": self.room.id,
				# "room_name": self.room.name,
				# "room_slug": self.room.slug,
				# "room_row": "room_" + str(self.room.id),
				# "room_count": self.room.num_participants,
			}
		)

	async def member_joining(self, event):		
		await self.send_json(
			{
				"msg_type": "member_joining",
				# "full_name": event["full_name"],
				"db_username": event["db_username"],
				"scope_username": event["scope_username"],				
				"username": event["username"],
				"card_title": event["card_title"],
				# "member_id": event["member_id"],
				# "role": event["role"],
				# "room_id": event["room_id"],
				# "room_name": event["room_name"],
				# "room_slug": event["room_slug"],
				# "room_row": event["room_row"],
				# "room_count": event["room_count"],
			},
		)


	async def leave_meeting_room(self):
		print("Disconnecting Status leave_meeting_room", str(self.scope["user"]))
		await self.channel_layer.group_send(
			self.socket_group_name,
			{
				'type': 'member_left',
				# "full_name": self.scope["user"].full_name,
				"db_username": self.user_db.username,
				"scope_username": self.scope["user"].username,
				"username": self.user.username,
				"card_title": self.card_title,
				# "member_id": self.scope["user"].id,
				# "role": self.role,
				# "room_id": self.room.id,
				# "room_name": self.room.name,
				# "room_slug": self.room.slug,
				# "room_row": "room_" + str(self.room.id),
				# "room_count": self.room.num_participants,
			}
		)

	async def member_left(self, event):		
		await self.send_json(
			{
				"msg_type": "member_left",
				# "full_name": event["full_name"],
				"db_username": event["db_username"],
				"scope_username": event["scope_username"],				
				"username": event["username"],
				"card_title": event["card_title"],
				# "member_id": event["member_id"],
				# "role": event["role"],
				# "room_id": event["room_id"],
				# "room_name": event["room_name"],
				# "room_slug": event["room_slug"],
				# "room_row": event["room_row"],
				# "room_count": event["room_count"],
			},
		)


@database_sync_to_async
def get_user_db(user_id):
    try:
        return CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return None