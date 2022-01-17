import json
import asyncio
from channels.db import database_sync_to_async


from channels.generic.websocket import AsyncJsonWebsocketConsumer
from asgiref.sync import async_to_sync
from django.utils import timezone

from channels.exceptions import StopConsumer
from users.models import CustomUser
from site_admin.models import Room
from reading_sessions.models import User_Status, Status_Redirect
from websockets.models import Websocket_Error

# from websockets.database_sync_to_async_functions import *

class StatusConsumer(AsyncJsonWebsocketConsumer):
	async def connect(self):
		print("\n\n\nStatusConsumer: connect: " + str(self.scope["user"]))
		self.socket_group_name = 'status'
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
		print("\n*******************StatusConsumer: disconnect", timezone.now())

		try:
			print("\n\nDisconnecting Status", str(self.scope["user"]))
			await set_user_offline(self.scope["user"])
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
		print("\n***** nStatusConsumer: receive_json: " + str(self.scope["user"]))
		# print("This is the command", command)

		if command =="join":
			await set_user_online(self.scope["user"], content)
			await self.join_meeting_room()

		elif command == "create_status_redirect":
			await create_status_redirect(content)



	async def join_meeting_room(self):
		await self.channel_layer.group_send(
			self.socket_group_name,
			{
				'type': 'member_joining',
				# "full_name": self.scope["user"].full_name,
				"username": self.scope["user"].username,
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
				"username": event["username"],
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
				"username": self.scope["user"].username,
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
				"username": event["username"],
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
def set_user_online(ini_user, content):
	try:
		print("\n\n\n\n\nset_user_online", ini_user.id, type(ini_user), content)
		if ini_user.id == content['member_id']:
			user = CustomUser.objects.get(id=ini_user.id)

		else:
			user = CustomUser.objects.get(id=content['member_id'])
			
		room = Room.objects.get(id=content['room_id'])
		print("\n\n\n\n\nSTATUS ROOM", room)
		user_status, created = User_Status.objects.get_or_create(user=user)
		user_status.online = True	
		user_status.in_room = room		
		user_status.all_connected = False
		user_status.max_reached = False
		user_status.has_ws_redirect = False
		user_status.has_status_redirect = False
		user_status.save()



	except Exception as e:
		print("BROKEN set_user_online", e)
		Websocket_Error.objects.create(file="_status_consumer.py",
						function_name="set_user_online",
						location_in_function="try block for set_user_online",
						occurred_for_user=user.username,
						error_text=e)
	return True	


@database_sync_to_async
def set_user_offline(user):
	try:
		user = CustomUser.objects.get(id=user.id)
		user_status, created = User_Status.objects.get_or_create(user=user)
		user_status.online = False
		user_status.in_room = None
		user_status.all_connected = False
		user_status.save()

	except Exception as e:
		print("BROKEN set_user_offline", e)
		Websocket_Error.objects.create(file="_status_consumer.py",
						function_name="set_user_online",
						location_in_function="try block for set_user_offline",
						occurred_for_user=user.username,
						error_text=e)
	return True	


@database_sync_to_async
def create_status_redirect(content):
	try:
		print("create_status_redirect", content)
		# user = CustomUser.objects.get(id=user.id)
		# user_status, created = User_Status.objects.get_or_create(user=user)
		# user_status.online = False
		# user_status.save()

	except Exception as e:
		print("BROKEN set_user_offline", e)
		Websocket_Error.objects.create(file="_status_consumer.py",
						function_name="set_user_online",
						location_in_function="try block for set_user_offline",
						occurred_for_user=user.username,
						error_text=e)
	return True	