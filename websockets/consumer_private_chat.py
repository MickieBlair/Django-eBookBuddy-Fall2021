from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.serializers import serialize
from django.utils import timezone
from django.core.paginator import Paginator

import json
import asyncio

from websockets.models import RoomChatMessage, PrivateChatRoom, UnreadChatRoomMessages

from websockets.serializers import LazyMeetingParticipantsEncoder
from websockets.serializers import LazyPrivateRoomChatMessageEncoder
from websockets.serializers import LazyCustomUserEncoder
from websockets.utils import calculate_timestamp
from websockets.exceptions import ClientError
from websockets.private_chat_constants import *
from users.models import CustomUser
from websockets.database_sync_to_async_functions import get_user_or_error
from websockets.database_sync_to_async_functions import private_get_connected_users
from websockets.database_sync_to_async_functions import create_private_chat_room_message
from websockets.database_sync_to_async_functions import append_unread_msg_if_not_connected

class ChatConsumer(AsyncJsonWebsocketConsumer):

	async def connect(self):
		"""
		Called when the websocket is handshaking as part of initial connection.
		"""
		# print("PRIVATE ChatConsumer: connect: " + str(self.scope["user"]))

		# let everyone connect. But limit read/write to authenticated users
		await self.accept()

		# the room_id will define what it means to be "connected". If it is not None, then the user is connected.
		self.room_id = None


	async def receive_json(self, content):
		"""
		Called when we get a text frame. Channels will JSON-decode the payload
		for us and pass it as the first argument.
		"""
		# Messages will have a "command" key we can switch on
		# print("PRIVATEChatConsumer: receive_json", content)
		command = content.get("command", None)
		try:
			if command == "join":
				# print("joining room: " + str(content['room']))
				await self.join_room(content["room"])
			elif command == "leave":
				# print("Leaving", content)
				await self.leave_room(content["room"])
			elif command == "send":
				# print('CONTENT in send', content)
				if len(content["message"].lstrip()) == 0:
					raise ClientError(422,"You can't send an empty message.")
				await self.send_room(content)


			elif command == "join_send_leave":
				# print("JOIN SEND LEAVE", content)
				self.room = await get_room_or_error(content['room_id'], self.scope["user"])
				# print(self.room)
				await connect_user(self.room, self.scope["user"])
				self.room_id = self.room.id
				if len(content["pvt_message"].lstrip()) == 0:
					raise ClientError(422,"You can't send an empty message.")
				await self.send_room_join_send_leave(self.room, self.scope["user"], content)
				await disconnect_user(self.room, self.scope["user"])

					

			elif command == "create_message":
				if len(content["pvt_message"].lstrip()) == 0:
					raise ClientError(422,"You can't send an empty message.")
				await self.send_room_not_connected(content)

			elif command == "get_room_chat_messages":
				await self.display_progress_bar(True)
				room = await get_room_or_error(content['room_id'], self.scope["user"])
				# print("** Room", room)
				try:
					payload = await get_room_chat_messages(room, content['page_number'])
					if payload != None:
						payload = json.loads(payload)
						await self.send_messages_payload(payload['messages'], payload['new_page_number'])
					else:
						raise ClientError(204,"Something went wrong retrieving the chatroom messages.")
					await self.display_progress_bar(False)
				except Exception as e:
					print("Exception get_room_chat_messages", e)

				


			elif command == "get_user_info":
				await self.display_progress_bar(True)
				room = await get_room_or_error(content['room_id'], self.scope["user"])
				payload = await get_user_info(room, self.scope["user"])
				if payload != None:
					payload = json.loads(payload)
					await self.send_user_info_payload(payload['user_info'])
				else:
					raise ClientError(204, "Something went wrong retrieving the other users account details.")
				await self.display_progress_bar(False)
		except ClientError as e:
			await self.handle_client_error(e)


	async def disconnect(self, code):
		"""
		Called when the WebSocket closes for any reason.
		"""
		# Leave the room
		# print("ChatConsumer: disconnect")
		try:
			if self.room_id != None:
				await self.leave_room(self.room_id)
		except Exception as e:
			print("EXCEPTION: disconnect" + str(e))
			pass


	async def join_room(self, room_id):
		"""
		Called by receive_json when someone sent a join command.
		"""
		# The logged-in user is in our scope thanks to the authentication ASGI middleware (AuthMiddlewareStack)
		# print("ChatConsumer: join_room: " + str(room_id))
		try:
			room = await get_room_or_error(room_id, self.scope["user"])
			# print("\n\n\n Private Room", room)
		except ClientError as e:
			return await self.handle_client_error(e)

		# Add user to "users" list for room
		await connect_user(room, self.scope["user"])

		# Store that we're in the room
		self.room_id = room.id
		# print("Self.room_id", self.room_id)

		await on_user_connected(room, self.scope["user"])

		# Add them to the group so they get room messages
		await self.channel_layer.group_add(
			room.group_name,
			self.channel_name,
		)

		# Instruct their client to finish opening the room
		await self.send_json({
			"join": str(room.id),
		})

		if self.scope["user"].is_authenticated:
			# Notify the group that someone joined
			await self.channel_layer.group_send(
				room.group_name,
				{
					"type": "chat.join",
					"room_id": room_id,
					"username": self.scope["user"].username,
					"user_id": self.scope["user"].id,
					"user_full_name": self.scope["user"].full_name,
					# "jitsi_room_name": self.scope["user"].user_location.room.name,
					# "jitsi_room_slug": self.scope["user"].user_location.room.slug,
				}
			)

	async def leave_room(self, room_id):
		"""
		Called by receive_json when someone sent a leave command.
		"""
		# The logged-in user is in our scope thanks to the authentication ASGI middleware
		# print("ChatConsumer: leave_room", room_id)

		room = await get_room_or_error(room_id, self.scope["user"])

		# Remove user from "connected_users" list
		await disconnect_user(room, self.scope["user"])

		# Notify the group that someone left
		await self.channel_layer.group_send(
			room.group_name,
			{
				"type": "chat.leave",
				"room_id": room_id,
				"username": self.scope["user"].username,
				"user_id": self.scope["user"].id,
				"user_full_name": self.scope["user"].full_name,
				# "jitsi_room_name": self.scope["user"].user_location.room.name,
				# "jitsi_room_slug": self.scope["user"].user_location.room.slug,
			}
		)

		# Remove that we're in the room
		self.room_id = None

		# Remove them from the group so they no longer get room messages
		await self.channel_layer.group_discard(
			room.group_name,
			self.channel_name,
		)
		# Instruct their client to finish closing the room
		await self.send_json({
			"leave": str(room.id),
		})



	async def send_room(self, content):
		"""
		Called by receive_json when someone sends a message to a room.
		"""
		# print("ChatConsumer: send_room", content)
		# Check they are in this room
		if self.room_id != None:
			if str(content['room_id']) != str(self.room_id):
				print("CLIENT ERRROR 1")
				raise ClientError("ROOM_ACCESS_DENIED", "Room access denied")
		else:
			print("CLIENT ERRROR 2")
			raise ClientError("ROOM_ACCESS_DENIED", "Room access denied")

		# Get the room and send to the group about it
		room = await get_room_or_error(content['room_id'], self.scope["user"])

		# print("******room", room)

		connected_users, user1, user2 = await private_get_connected_users(room)

		message = await create_private_chat_room_message(room, self.scope["user"], content)

		# Execute these functions asychronously
		await asyncio.gather(*[
			append_unread_msg_if_not_connected(self.scope["user"], room, user1, connected_users, message), 
			append_unread_msg_if_not_connected(self.scope["user"], room, user2, connected_users, message),

		])

		await self.channel_layer.group_send(
			room.group_name,
			{
				"type": "chat.message",
				"username": self.scope["user"].username,
				"user_id": self.scope["user"].id,
				"user_full_name": self.scope["user"].full_name,
				# "jitsi_room_name": self.scope["user"].user_location.room.name,
				# "jitsi_room_slug": self.scope["user"].user_location.room.slug,
				"message": message.content,
				"room_id": content['room_id'],
				"to_user": content['to_user']
			}
		)


	# These helper methods are named by the types we send - so chat.join becomes chat_join
	async def chat_join(self, event):
		"""
		Called when someone has joined our chat.
		"""
		# Send a message down to the client
		# print("ChatConsumer: chat_join: " + str(self.scope["user"].id))
		if event["username"]:
			await self.send_json(
				{
					"msg_type": PRIVATE_MSG_TYPE_ENTER,
					"room": event["room_id"],
					"username": event["username"],
					"user_id": event["user_id"],
					"user_full_name": event["user_full_name"],
					# "jitsi_room_name": event["jitsi_room_name"],
					# "jitsi_room_slug": event["jitsi_room_slug"],
					"message": event["username"] + " connected.",
				},
			)

	async def chat_leave(self, event):
		"""
		Called when someone has left our chat.
		"""
		# Send a message down to the client
		# print("ChatConsumer: chat_leave")
		if event["username"]:
			await self.send_json(
			{
				"msg_type": PRIVATE_MSG_TYPE_LEAVE,
				"room": event["room_id"],
				"username": event["username"],
				"user_id": event["user_id"],
				"user_full_name": event["user_full_name"],
				# "jitsi_room_name": event["jitsi_room_name"],
				# "jitsi_room_slug": event["jitsi_room_slug"],
				"message": event["username"] + " disconnected.",
			},
		)


	async def chat_message(self, event):
		"""
		Called when someone has messaged our chat.
		"""
		# Send a message down to the client
		# print("ChatConsumer: chat_message")

		timestamp = calculate_timestamp(timezone.now())

		await self.send_json(
			{
				"msg_type": PRIVATE_MSG_TYPE_MESSAGE,
				"username": event["username"],
				"user_id": event["user_id"],
				"user_full_name": event["user_full_name"],
				# "jitsi_room_name": event["jitsi_room_name"],
				# "jitsi_room_slug": event["jitsi_room_slug"],
				"message": event["message"],
				"natural_timestamp": timestamp,
				"to_user": event['to_user'],
			},
		)

	async def send_messages_payload(self, messages, new_page_number):
		"""
		Send a payload of messages to the ui
		"""
		# print("ChatConsumer: send_messages_payload. ")

		await self.send_json(
			{
				"messages_payload": "messages_payload",
				"messages": messages,
				"new_page_number": new_page_number,
			},
		)

	async def send_user_info_payload(self, user_info):
		"""
		Send a payload of user information to the ui
		"""
		# print("ChatConsumer: send_user_info_payload. ")
		await self.send_json(
			{
				"user_info": user_info,
			},
		)

	async def display_progress_bar(self, is_displayed):
		"""
		1. is_displayed = True
		- Display the progress bar on UI
		2. is_displayed = False
		- Hide the progress bar on UI
		"""
		# print("DISPLAY PROGRESS BAR: " + str(is_displayed))
		await self.send_json(
			{
				"display_progress_bar": is_displayed
			}
		)


	async def handle_client_error(self, e):
		"""
		Called when a ClientError is raised.
		Sends error data to UI.
		"""
		errorData = {}
		errorData['error'] = e.code
		if e.message:
			errorData['message'] = e.message
			await self.send_json(errorData)
		return


@database_sync_to_async
def get_room_or_error(room_id, user):
	"""
	Tries to fetch a room for the user, checking permissions along the way.
	"""
	try:
		room = PrivateChatRoom.objects.get(pk=room_id)
		user1 = room.user1
		user2 = room.user2
		if user != user1 and user != user2:
			raise ClientError("ROOM_ACCESS_DENIED", "You do not have permission to join this room.")
		# else:
		# 	print("Allowed")

	except Exception as e:
		print('Broken get_room_or_error', e)

	return room


# I don't think this requires @database_sync_to_async since we are just accessing a model field
# https://docs.djangoproject.com/en/3.1/ref/models/instances/#refreshing-objects-from-database
@database_sync_to_async
def get_user_info(room, user):
	"""
	Retrieve the user info for the user you are chatting with
	"""
	try:
		# Determine who is who
		other_user = room.user1
		if other_user == user:
			other_user = room.user2

		payload = {}
		s = LazyCustomUserEncoder()
		# convert to list for serializer and select first entry (there will be only 1)
		payload['user_info'] = s.serialize([other_user])[0] 
		return json.dumps(payload)
	except ClientError as e:
		raise ClientError("DATA_ERROR", "Unable to get that users information.")
	return None


@database_sync_to_async
def create_room_chat_message(room, user, content):
	message = ""
	# print("create_room_chat_message")
	# print('room', room)
	# print('user', user)
	# print('content', content)
	to_user = CustomUser.objects.get(id=content['to_user'])

	message = RoomChatMessage.objects.create(from_user= user,
											to_user=to_user,
											user=user,
											room=room,
											content=content['pvt_message'])
	return message


@database_sync_to_async
def get_room_chat_messages(room, page_number):
	# print("room, page_number", room, page_number)
	try:
		qs = RoomChatMessage.objects.by_room(room)
		p = Paginator(qs, PRIVATE_DEFAULT_ROOM_CHAT_MESSAGE_PAGE_SIZE)

		payload = {}
		messages_data = None
		new_page_number = int(page_number)  
		if new_page_number <= p.num_pages:
			new_page_number = new_page_number + 1
			s = LazyPrivateRoomChatMessageEncoder()
			payload['messages'] = s.serialize(p.page(page_number).object_list)
		else:
			payload['messages'] = "None"
		payload['new_page_number'] = new_page_number
		return json.dumps(payload)
	except Exception as e:
		print("EXCEPTION get_room_chat_messages: " + str(e))
	return None
	
# @database_sync_to_async
# def get_room_chat_messages(room, jitsi_room, page_number):
# 	try:
# 		qs = Jitsi_Room_Chat_Message.objects.by_room(room, jitsi_room)
# 		p = Paginator(qs, JITSI_DEFAULT_ROOM_CHAT_MESSAGE_PAGE_SIZE)

# 		payload = {}
# 		messages_data = None
# 		new_page_number = int(page_number)  
# 		if new_page_number <= p.num_pages:
# 			new_page_number = new_page_number + 1
# 			s = LazyJitsiRoomChatMessageEncoder()
# 			payload['messages'] = s.serialize(p.page(page_number).object_list)
# 		else:
# 			payload['messages'] = "None"
# 		payload['new_page_number'] = new_page_number
# 		return json.dumps(payload)
# 	except Exception as e:
# 		print("EXCEPTION: " + str(e))
# 		return None


@database_sync_to_async
def connect_user(room, user):
	# add user to connected_users list
	user = CustomUser.objects.get(pk=user.id)
	# print("User", user)
	return room.connect_user(user)


@database_sync_to_async
def disconnect_user(room, user):
	# remove from connected_users list
	user = CustomUser.objects.get(pk=user.id)
	return room.disconnect_user(user)


# @database_sync_to_async
# def get_connected_users(room):
# 	try:
# 		connected_users = room.connected_users.all()
# 		user1 = room.user1
# 		user2 = room.user2		
# 		# print("count", count)	
# 	except:
# 		print("\n\n\nBROKEN get_connected_users")
# 	return connected_users, user1, user2


# If the user is not connected to the chat, increment "unread messages" count
# @database_sync_to_async
# def append_unread_msg_if_not_connected(sender, room, user, connected_users, message):
# 	if not user in connected_users: 
# 		try:
# 			unread_msgs = UnreadChatRoomMessages.objects.get(room=room, user=user)
# 			unread_msgs.most_recent_message = message.content
# 			unread_msgs.last_message = message
# 			unread_msgs.count += 1
# 			unread_msgs.save()
# 			unread_msgs.unread_msgs.add(message)
# 		except UnreadChatRoomMessages.DoesNotExist:
# 			UnreadChatRoomMessages(room=room, user=user,
# 									count=1, most_recent_message=message.content,
# 									last_message=message).save()
# 			pass
# 	return


	# try:
	# 	if sender != user:
	# 		print("this user needs the unread", sender, user)
	# 		if UnreadChatRoomMessages.objects.filter(room=room, user=user).exists():
	# 			print("Exists")
	# 			unread_msgs = UnreadChatRoomMessages.objects.get(room=room, user=user)
	# 			unread_msgs.most_recent_message = message
	# 			unread_msgs.count += 1
	# 			unread_msgs.save()
	# 		else:
	# 			print("Create")
	# 			new_unread = UnreadChatRoomMessages.objects.create(room=room, user = user, count=1)
	# 			print(new_unread)
	# 	else:
	# 		print("this one doesn't", sender, user)

		# if not user in connected_users: 
		# 	if UnreadChatRoomMessages.objects.filter(room=room, user=user).exists():
		# 		print("Exists")
		# 	else:
		# 		print("Create")
		# 		new_unread = UnreadChatRoomMessages.objects.create(room=room, user = user, count=1)
		# 		print(new_unread)
			# try:
			# 	unread_msgs = UnreadChatRoomMessages.objects.get(room=room, user=user)
			# 	print(unread_msgs)
			# 	unread_msgs.most_recent_message = message
			# 	unread_msgs.count += 1
			# 	unread_msgs.save()

			# except UnreadChatRoomMessages.DoesNotExist:
			# 	print("\n\n\n\nEXCEPT HERE")
			# 	new_unread = UnreadChatRoomMessages.objects.create(room=room, user=user, count = 1)
				
			# 	# UnreadChatRoomMessages(room=room, user=user, count=1).save()
			# 	pass
		# return
	# except Exception as e:
	# 	print("\n\n***********Broken", e)
	

# When a user connects, reset their unread message count
@database_sync_to_async
def on_user_connected(room, user):
	# print("On user connected", room, user)
	# confirm they are in the connected users list
	connected_users = room.connected_users.all()
	# print("connected_user", connected_users)
	if user in connected_users:
		# print("yes in connected users")
		try:
			# reset count
			unread_msgs = UnreadChatRoomMessages.objects.get(room=room, user=user)
			# print("unread_msgs count before", unread_msgs.count)
			unread_msgs.count = 0
			unread_msgs.save()
			# print("unread_msgs count after", unread_msgs.count)
		except UnreadChatRoomMessages.DoesNotExist:
			UnreadChatRoomMessages(room=room, user=user).save()
			pass

	else:
		print("No not in connected users")
	return


	# async def send_room_join_send_leave(self, room, user, content):
	# 	"""
	# 	Called by receive_json when someone sends a message to a room.
	# 	"""
	# 	print("ChatConsumer: send_room_join_send_leave")
	# 	# Check they are in this room
	# 	# self.user, self.role= await get_user_or_error(str(self.scope["user"]))

	# 	if self.room_id != None:
	# 		if str(content['room_id']) != str(self.room_id):
	# 			print("CLIENT ERRROR 1")
	# 			raise ClientError("ROOM_ACCESS_DENIED", "Room access denied")
	# 	else:
	# 		print("CLIENT ERRROR 2")
	# 		raise ClientError("ROOM_ACCESS_DENIED", "Room access denied")

	# 	# # Get the room and send to the group about it
	# 	# room = await get_room_or_error(room_id, self.scope["user"])

	# 	# get list of connected_users
	# 	connected_users, user1, user2 = await private_get_connected_users(room)
	# 	message = await create_room_chat_message(room, self.scope["user"], content)

	# 	# Execute these functions asychronously
	# 	await asyncio.gather(*[
	# 		append_unread_msg_if_not_connected(self.scope["user"], room, user1, connected_users, message), 
	# 		append_unread_msg_if_not_connected(self.scope["user"], room, user2, connected_users, message),

	# 	])

	# 	await self.channel_layer.group_send(
	# 		room.group_name,
	# 		{
	# 			"type": "chat.message",
	# 			"username": self.scope["user"].username,
	# 			"user_id": self.scope["user"].id,
	# 			"user_full_name": self.scope["user"].full_name,
	# 			# "jitsi_room_id": self.user.user_location.room.id,
	# 			# "jitsi_room_name": self.user.user_location.room.name,
	# 			# "jitsi_room_slug": self.user.user_location.room.slug,
	# 			"to_user": message.to_user.id,
	# 			"from_user": message.from_user.id,
	# 			"pvt_message": message.content,
	# 			"room_id": self.room_id,
	# 		}
	# 	)

		





	# async def send_room_not_connected(self, content):
	# 	"""
	# 	Called by receive_json when someone sends a message to a room.
	# 	"""
	# 	room_id = content['room']
	# 	message = content['pvt_message']


	# 	print("ChatConsumer: send_room_not_connected")

	# 	# Get the room and send to the group about it
	# 	self.pvt_room = await get_room_or_error(room_id, self.scope["user"])
	# 	print(self.pvt_room)

	# 	connected_users, user1, user2 = await get_connected_users(self.pvt_room)

	# 	# # self.

	# 	# # Check they are in this room
	# 	# if self.room_id != None:
	# 	# 	if str(room_id) != str(self.room_id):
	# 	# 		print("CLIENT ERRROR 1")
	# 	# 		raise ClientError("ROOM_ACCESS_DENIED", "Room access denied")
	# 	# else:
	# 	# 	print("CLIENT ERRROR 2")
	# 	# 	raise ClientError("ROOM_ACCESS_DENIED", "Room access denied")

		

	# 	# # get list of connected_users
	# 	# connected_users = room.connected_users.all()
		


	# 	# Execute these functions asychronously
	# 	# await asyncio.gather(*[
	# 	# 	append_unread_msg_if_not_connected(self.scope["user"], self.pvt_room, user1, connected_users, message), 
	# 	# 	append_unread_msg_if_not_connected(self.scope["user"], self.pvt_room, user2, connected_users, message),
			
	# 	# ])

	# 	# await self.channel_layer.group_send(
	# 	# 	room.group_name,
	# 	# 	{
	# 	# 		"type": "chat.message",
	# 	# 		"username": self.scope["user"].username,
	# 	# 		"user_id": self.scope["user"].id,
	# 	# 		"user_full_name": self.scope["user"].full_name,
	# 	# 		"jitsi_room_name": self.scope["user"].user_location.room.name,
	# 	# 		"jitsi_room_slug": self.scope["user"].user_location.room.slug,
	# 	# 		"message": message,
	# 	# 		"room_id": room_id,
	# 	# 	}
	# 	# )














