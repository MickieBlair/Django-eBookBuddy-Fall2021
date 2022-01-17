import json
import asyncio
from channels.db import database_sync_to_async

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from asgiref.sync import async_to_sync
from django.utils import timezone

from channels.exceptions import StopConsumer

from jitsi_data.jitsi_database_async import *

class JitsiConsumer(AsyncJsonWebsocketConsumer):
	async def connect(self):
		print("\n\n\n JitsiConsumer: connect: " + str(self.scope["user"]))
		self.socket_group_name = 'jitsi_data'
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
		print("\n*******************JitsiConsumer: disconnect", timezone.now())

		try:
			print("Disconnecting JitsiConsumer", str(self.scope["user"]))
			await self.disconnect_meeting_room()
		
		except Exception as e:
			socket_info={}
			socket_info['file']="consumer_jitsi.py"
			socket_info['function_name']="websocket_disconnect"
			socket_info['location_in_function']="Disconnecting JitsiConsumer"
			socket_info['occurred_for_user']=str(self.scope["user"])
			socket_info['error_text']=str(e) 
			await create_log_of_error(socket_info)

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
		print("\n***** JitsiConsumer: receive_json: " + str(self.scope["user"]))
		print("This is the content", content)
		
		if command =="join_jitsi":
			await self.join_meeting_room(content)

		elif command =="leave_jitsi":
			await self.leave_meeting_room(content)

		elif command == "in_room":
			await self.set_room_participants(content)

		elif command == "api_get_room_participants":
			await reset_room(content['sender_id'], content['room_id'])
			await self.api_get_room_participants(content)

		elif command == "api_set_room_participants":
			await self.api_set_room_participants(content)

			


	async def join_meeting_room(self, content):
		jitsi_room = content['jitsi_room']
		room_name = content['room_name']
		member_id = content['member_id']
		jitsi_id = content['jitsi_id']		
		display_name = content['display_name']
		self.room_name = content['room_name']

		self.user = await get_user(member_id)
		status = await join_set_room_and_jitsi_status(self.user, jitsi_id, member_id,
													display_name, jitsi_room, room_name)
		# print("Self.user", self.user)
		print("join_meeting_room.status", status)


		await self.channel_layer.group_send(
			self.socket_group_name,
			{
				'type': 'jitsi_joining',
				"username": self.user.username,
				"status": status,				
			}
		)

	async def jitsi_joining(self, event):		
		await self.send_json(
			{
				"msg_type": "jitsi_join",			
				"username": event["username"],
				"status": event["status"],				
			},
		)

	async def leave_meeting_room(self, content):
		print("\n\n\n\n!!!!!!!!!!!Disconnecting Jitsi leave_meeting_room", str(self.scope["user"]))
		jitsi_room = content['jitsi_room']
		room_name = content['room_name']
		member_id = content['member_id']
		jitsi_id = content['jitsi_id']		
		display_name = content['display_name']

		self.user = await get_user(member_id)
		status = await leave_set_room_and_jitsi_status(self.user, jitsi_id, member_id,
													display_name, jitsi_room, room_name)
		print("leave_meeting_room.status", status)

		await self.channel_layer.group_send(
			self.socket_group_name,
			{
				'type': 'jitsi_leave',
				"username": self.user.username,
				"status": status,
			}
		)


	async def disconnect_meeting_room(self):
		print("\n\n\n\n\n!!!!!CLOSE WINDOW Jitsi disconnect_meeting_room", str(self.scope["user"]), self.room_name)
		try:
			print("self.scope[user].id", self.scope["user"].id)
			if self.user:
				print("The user", self.user)
				send_data, status = await disconnect_set_room_and_jitsi_status(self.user, self.room_name)
			else:
				self.user = await get_user(self.scope["user"].id)
				print("Now the user is", self.user)
				send_data, status = await disconnect_set_room_and_jitsi_status(self.user, self.room_name)
		except Exception as e:
			print("Broken disconnect_meeting_room")


		await self.channel_layer.group_send(
			self.socket_group_name,
			{
				'type': 'disconnect_user',
				"username": self.user.username,
				"post_data": send_data,
				"status": status,
			}
		)

	async def jitsi_leave(self, event):		
		await self.send_json(
			{
				"msg_type": "jitsi_left",			
				"username": event["username"],
				"status": event["status"],
			},
		)

	async def disconnect_user(self, event):		
		await self.send_json(
			{
				"msg_type": "disconnect_user",			
				"username": event["username"],
				"post_data": event["post_data"],
				"status": event["status"],
			},
		)

	async def api_set_room_participants(self, content):
		print("\n\n\n*************api_set_room_participants Jitsi", str(self.scope["user"]))
		room_id = content['room_id']
		room_participants = content['room_participants']
		# joining = content['joining']
		sender_id = content['sender_id']

		api_data = await api_set_room_participants(sender_id,room_id, room_participants)

		await self.channel_layer.group_send(
			self.socket_group_name,
			{
				'type': 'room_participants_api',
				'room_id': room_id,
				'room_participants': api_data,
			}
		)

	async def room_participants_api(self, event):
		print("\n\n\n sending room_participants_api", event)		
		await self.send_json(
			{
				"msg_type": "updated_room_participants",	
				"room_id": event["room_id"],
				"room_participants": event["room_participants"],		
			},
		)



	async def api_get_room_participants(self, content):
		print("api_get_room_participants Jitsi", str(self.scope["user"]))
		to_get_room_id = content['room_id']
		# participants = content['participants']
		# joining = content['joining']
		# sender_id = content['sender_id']

		# self.participants = await db_set_room_participants(jitsi_room, participants, joining, sender_id)

		await self.channel_layer.group_send(
			self.socket_group_name,
			{
				'type': 'api_call_for_participants',
				'to_get_room_id': to_get_room_id,
			}
		)

	async def api_call_for_participants(self, event):
		print("\n\n\n sending api_call_for_participants", event)		
		await self.send_json(
			{
				"msg_type": "api_call_for_participants",	
				"to_get_room_id": event["to_get_room_id"],		
			},
		)



	async def set_room_participants(self, content):
		print("set_room_participants Jitsi", str(self.scope["user"]))
		jitsi_room = content['jitsi_room']
		participants = content['participants']
		joining = content['joining']
		sender_id = content['sender_id']

		self.participants = await db_set_room_participants(jitsi_room, participants, joining, sender_id)

		await self.channel_layer.group_send(
			self.socket_group_name,
			{
				'type': 'api_participants',
				'roomName': jitsi_room,
				"participants": participants,
				"data": self.participants,
			}
		)

	async def api_participants(self, event):
		print("\n\n\n sending api_participants", event)		
		await self.send_json(
			{
				"msg_type": "api_participants",	
				"roomName": event["roomName"],		
				"participants": event["participants"],
				"data": event["data"],
			},
		)


