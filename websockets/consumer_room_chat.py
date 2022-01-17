from django.core.serializers.python import Serializer
from django.core.paginator import Paginator
from django.core.serializers import serialize
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
import json
from django.utils import timezone

from websockets.room_chat_constants import *
from site_admin.models import Room
from websockets.models import Jitsi_Chat_Room, Jitsi_Room_Chat_Message
from websockets.models import Jitsi_Room_Unread_Chat_Message, Room_Chat_Error
from websockets.exceptions import ClientError
from websockets.utils import calculate_timestamp

from websockets.serializers import LazyJitsiRoomChatMessageEncoder
from websockets.serializers import LazyRoomUnreadEncoder, LazyMeetingParticipantsEncoder


# Example taken from:
# https://github.com/andrewgodwin/channels-examples/blob/master/multichat/chat/consumers.py
class PublicChatConsumer(AsyncJsonWebsocketConsumer):

	async def connect(self):
		"""
		Called when the websocket is handshaking as part of initial connection.
		"""
		print("\n\n\n@@@@@@@@@@@@@@@@@@@@@PublicChatConsumer: connect: " + str(self.scope["user"]))
		# let everyone connect. But limit read/write to authenticated users
		await self.accept()
		self.room_id = None
		

	async def disconnect(self, code):
		"""
		Called when the WebSocket closes for any reason.
		"""
		# leave the room
		# print("PublicChatConsumer: disconnect")
		try:
			if self.room_id != None:
				await self.leave_room(self.room_id)
		except Exception:
			pass


	async def receive_json(self, content):
		"""
		Called when we get a text frame. Channels will JSON-decode the payload
		for us and pass it as the first argument.
		"""
		# Messages will have a "command" key we can switch on
		command = content.get("command", None)
		print("PublicChatConsumer: receive_json: " + str(command))
		# print("\n\n\n*****Joining", content)
		try:
			if command == "send":
				if len(content["message"].lstrip()) != 0:
					await self.send_room(content["room_id"], content["message"],
										content['meeting_room'], content['meeting_room_id'])
					# raise ClientError(422,"You can't send an empty message.")
			elif command == "join":
				# Make them join the room
				print("\n\n\n*****Joining ROOM CHAT JSON", content)
				await self.join_room(content["room"], content['jitsi_room'])
			elif command == "leave":
				# Leave the room
				await self.leave_room(content["room"])
			elif command == "get_room_chat_messages":
				# print('\n\n\n*****get room messages', content, self.jitsi_room)

				# send the new user count to the room
				try:
					# print("\n\n\n^^^^^^^^^^^^^^^^^^get_room_chat_messages")
					num_connected_users, users_in_room = await get_num_connected_users(self.jitsi_room)
					await self.channel_layer.group_send(
						self.chat_room.group_name,
						{
							"type": "connected.user.count",
							"connected_user_count": num_connected_users,
							"jitsi_room_users": self.jitsi_room.num_participants,
							"users_in_room": users_in_room,
						}
					)
				except Exception as e:
					print("BRoken join_room num_connected_users", e)
				
				await self.display_progress_bar(True)
				# room = await get_room_or_error(content['room_id'])

				payload = await get_room_chat_messages(self.chat_room, self.jitsi_room,
										content['page_number'])
				unread_counts = await get_unread_counts(self.scope["user"], self.jitsi_room )
				# print("\n\n\n****unread_counts", unread_counts)
				if payload != None:
					payload = json.loads(payload)
					await self.send_messages_payload(payload['messages'],
										payload['new_page_number'], unread_counts)
				else:
					raise ClientError(204,"Something went wrong retrieving the chatroom messages.")
				await self.display_progress_bar(False)

		except ClientError as e:
			socket_info={}
			socket_info['file']="consumer_room_chat.py"
			socket_info['function_name']="receive_json"
			socket_info['location_in_function']="try block receive_json"
			socket_info['occurred_for_user']=str(self.scope["user"])
			socket_info['error_text']=str(e)
			await create_log_of_error(socket_info)
			await self.display_progress_bar(False)
			await self.handle_client_error(e)


	async def send_room(self, room_id, message, meeting_room, meeting_room_id):
		"""
		Called by receive_json when someone sends a message to a room.
		"""
		# Check they are in this room
		# print("PublicChatConsumer: send_room")
		print("in send room room_id", room_id)
		print("self.room_id", self.room_id)
		if self.room_id != None:
			
			if str(room_id) != str(self.room_id):
				print("Room ID", room_id)
				print("Self.room_id", self.room_id)
				raise ClientError("ROOM_ACCESS_DENIED", "Room access denied")
			if not is_authenticated(self.scope["user"]):
				raise ClientError("AUTH_ERROR", "You must be authenticated to chat.")
		else:
			raise ClientError("ROOM_ACCESS_DENIED", "Room access denied")

		# Get the room and send to the group about it
		# room = await get_room_or_error(room_id)
		await create_public_room_chat_message(self.chat_room, self.scope["user"], message, meeting_room_id)
		unread_counts = await get_unread_counts(self.scope["user"], self.jitsi_room)

		await self.channel_layer.group_send(
			self.chat_room.group_name,
			{
				"type": "chat.message",
				# "profile_image": self.scope["user"].profile_image.url,
				"username": self.scope["user"].username,
				"user_id": self.scope["user"].id,
				"meeting_room_id": meeting_room_id,
				"meeting_room_name": meeting_room,
				"message": message,
				"unread_counts": unread_counts,				
			}
		)

	async def chat_message(self, event):
		"""
		Called when someone has messaged our chat.
		"""
		# Send a message down to the client
		# print("**********EVENT",event)
		# print("PublicChatConsumer: chat_message from user #" + str(event["user_id"]))
		timestamp = calculate_timestamp(timezone.now())
		await self.send_json(
			{
				"msg_type": JITSI_MSG_TYPE_MESSAGE,
				# "profile_image": event["profile_image"],
				"username": event["username"],
				"user_id": event["user_id"],
				"message": event["message"],
				"meeting_room_id": event["meeting_room_id"],
				"meeting_room_name": event["meeting_room_name"],
				"natural_timestamp": timestamp,
				"room_msg_counts": event["unread_counts"],
			},
		)

	async def join_room(self, room_id, jitsi_room_id):
		print("************Joining room_id", room_id)
		print("++++++++++++Joining jitsi_room_id", jitsi_room_id)
		"""
		Called by receive_json when someone sent a join command.
		"""
		# print("PublicChatConsumer: join_room")
		is_auth = is_authenticated(self.scope["user"])
		try:
			self.chat_room, self.jitsi_room = await get_room_or_error(room_id, jitsi_room_id) 
		except ClientError as e:
			await self.handle_client_error(e)

		# Add user to "users" list for room
		if is_auth:
			await connect_user(self.chat_room, self.scope["user"])



		# Store that we're in the room
		self.room_id = self.chat_room.id

		# Add them to the group so they get room messages
		await self.channel_layer.group_add(
			self.chat_room.group_name,
			self.channel_name,
		)

		# Instruct their client to finish opening the room
		await self.send_json({
			"join": str(self.chat_room)
		})

		


	async def leave_room(self, room_id):
		"""
		Called by receive_json when someone sent a leave command.
		"""
		# print("PublicChatConsumer: leave_room", self.scope["user"])
		is_auth = is_authenticated(self.scope["user"])
		# print("is_auth", is_auth)
		try:
			room, jitsi_room = await get_room_or_error(room_id, self.jitsi_room.id )
			# print("room", room)
		except Exception as e:
			print("@@@@@ Exception room", e)

		


		# Remove user from "users" list
		if is_auth:
			await disconnect_user(room, self.scope["user"], jitsi_room)

		# Remove that we're in the room
		self.room_id = None
		# Remove them from the group so they no longer get room messages
		await self.channel_layer.group_discard(
			room.group_name,
			self.channel_name,
		)

		# send the new user count to the room
		# print("\n\n\n^^^^^^^^^^^^^^^^^^leave_room")
		num_connected_users, users_in_room = await get_num_connected_users(self.jitsi_room)
		await self.channel_layer.group_send(
		room.group_name,
			{
				"type": "connected.user.count",
				"connected_user_count": num_connected_users,
				"jitsi_room_users": self.jitsi_room.num_participants,
				"users_in_room": users_in_room,
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

	async def send_messages_payload(self, messages, new_page_number, unread_counts):
		"""
		Send a payload of messages to the ui

		"""

		# print("\n\n\n\n!!!!!!!!!!!PublicChatConsumer: send_messages_payload. ")
		# print(unread_counts)

		await self.send_json(
			{
				"messages_payload": "messages_payload",
				"messages": messages,
				"new_page_number": new_page_number,
				"unread_counts": unread_counts,
			},
		)

	async def connected_user_count(self, event):
		"""
		Called to send the number of connected users to the room.
		This number is displayed in the room so other users know how many users are connected to the chat.
		"""
		# Send a message down to the client
		# print("PublicChatConsumer: connected_user_count: count: " + str(event["connected_user_count"]))
		await self.send_json(
			{
				"msg_type": JITSI_MSG_TYPE_CONNECTED_USER_COUNT,
				"connected_user_count": event["connected_user_count"],
				"jitsi_room_users": event["jitsi_room_users"],
				"users_in_room": event["users_in_room"],
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


def is_authenticated(user):
	if user.is_authenticated:
		return True
	return False

@database_sync_to_async
def get_unread_counts(user, jitsi_room):
	# print("/********************GET UNREAD COUNTS", user, jitsi_room)

	room = user.session_status.room
	
	if room:
		# print('\n\n\n\n\n**********************HAS room', room)
		participants = room.participants.all()
		for user in participants:
			unread = Jitsi_Room_Unread_Chat_Message.objects.get_or_create(user=user)
	else:
		# print('\n\n\n\n\n**********************HAS NO room', jitsi_room, type(jitsi_room))
		participants = jitsi_room.participants.all()
		for user in participants:
			unread = Jitsi_Room_Unread_Chat_Message.objects.get_or_create(user=user)




	payload = {}
	s = LazyRoomUnreadEncoder()
	payload['room_unread_counts'] = s.serialize(participants)
	data = json.dumps(payload)
	return data

@database_sync_to_async
def get_num_connected_users(room):
	try:
		# print("****************room", room, type(room))
		# room = Chat_Room.objects.get(pk=room_id)
		count= len(room.participants.all())
		
		participants = room.participants.all()

		payload = {}
		s = LazyMeetingParticipantsEncoder()
		payload['chat_participants'] = s.serialize(participants)
		data = json.dumps(payload)
		
		# print("data", data)
		# print("count", count)		
	except Exception as e:
		print("\n\n\nBROKEN get_user_count_in_room", e)
	return count, data

@database_sync_to_async
def create_public_room_chat_message(room, user, message, meeting_room_id):
	try:
		print("create_public_room_chat_message", room, user, message)

		# user_room = user.session_status.room
		
		page = Room.objects.get(id=meeting_room_id)
		print("USER ROOM", page)
		participants = page.participants.all().exclude(id=user.id)

		for part in participants:
			unread, created = Jitsi_Room_Unread_Chat_Message.objects.get_or_create(user=part)
			unread.add_one(user.session_status.room)

		# all_staff = CustomUser.objects.filter(role__name = "Staff").exclude(id=user.id)
		# for member in all_staff:
		# 	member.unread_staff.add_one()

		message = Jitsi_Room_Chat_Message.objects.create(user=user, room=room,
						meeting_room= page, content=message)
		# all_staff_counts = CustomUser.objects.filter(role__name = "Staff")
		# payload = {}
		# s = LazyStaffEncoder()
		# payload['all_staff_counts'] = s.serialize(all_staff_counts)
		# data = json.dumps(payload)
		
	    # return Jitsi_Room_Chat_Message.objects.create(user=user, room=room, content=message)


	except Exception as e:
		socket_info={}
		socket_info['file']="consumer_room_chat.py"
		socket_info['function_name']="database_sync_to_async create_public_room_chat_message"
		socket_info['location_in_function']="database_sync_to_async create_public_room_chat_message"
		socket_info['occurred_for_user']=str(self.scope["user"])
		socket_info['error_text']=str(e)
		Staff_Chat_Error.objects.create(file=socket_info['file'],
						function_name=socket_info['function_name'],
						location_in_function=socket_info['location_in_function'],
						occurred_for_user=socket_info['occurred_for_user'],
						error_text=socket_info['error_text'])
	

	return message
@database_sync_to_async
def connect_user(room, user):
	is_added, jitsi_room = room.connect_user(user)
	return jitsi_room

@database_sync_to_async
def disconnect_user(room, user, jitsi_room):
	print("***********disconnect room chat", user, room)
	try:
		return room.disconnect_user(user, jitsi_room)
	except Exception as e:
		print('Exception', e)
	

@database_sync_to_async
def get_room_or_error(room_id, jitsi_room_id):
	"""
	Tries to fetch a room for the user
	"""
	try:
		chat_room = Jitsi_Chat_Room.objects.get(pk=room_id)
		jitsi_room = Room.objects.get(pk=jitsi_room_id)
	except Exception as e:
		print("Joining a Room chat Exception", e)
	return chat_room, jitsi_room


@database_sync_to_async
def get_room_chat_messages(room, jitsi_room, page_number):
	try:
		# jitsi_room = Room.objects.get(id=jitsi_room)
		qs = Jitsi_Room_Chat_Message.objects.by_room(room.id, jitsi_room.id)
		p = Paginator(qs, JITSI_DEFAULT_ROOM_CHAT_MESSAGE_PAGE_SIZE)

		payload = {}
		messages_data = None
		new_page_number = int(page_number)  
		if new_page_number <= p.num_pages:
			new_page_number = new_page_number + 1
			s = LazyJitsiRoomChatMessageEncoder()
			payload['messages'] = s.serialize(p.page(page_number).object_list)
		else:
			payload['messages'] = "None"
		payload['new_page_number'] = new_page_number
		return json.dumps(payload)
	except Exception as e:
		print("EXCEPTION: get_room_chat_messages " + str(e))
		return None

@database_sync_to_async
def create_log_of_error(socket_info):
	try:
		Room_Chat_Error.objects.create(file=socket_info['file'],
						function_name=socket_info['function_name'],
						location_in_function=socket_info['location_in_function'],
						occurred_for_user=socket_info['occurred_for_user'],
						error_text=socket_info['error_text'])

	except Exception as e:
		print("\n\n\nBROKEN create_log_of_error")



# class LazyRoomChatMessageEncoder(Serializer):
# 	def get_dump_object(self, obj):
# 		dump_object = {}
# 		dump_object.update({'msg_type': JITSI_MSG_TYPE_MESSAGE})
# 		dump_object.update({'msg_id': str(obj.id)})
# 		dump_object.update({'user_id': str(obj.user.id)})
# 		dump_object.update({'username': str(obj.user.username)})
# 		dump_object.update({'message': str(obj.content)})
# 		# dump_object.update({'profile_image': str(obj.user.profile_image.url)})
# 		dump_object.update({'natural_timestamp': calculate_timestamp(obj.timestamp)})
# 		return dump_object
















