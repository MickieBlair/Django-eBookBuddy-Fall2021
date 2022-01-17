from django.core.serializers.python import Serializer
from django.core.paginator import Paginator
from django.core.serializers import serialize
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.exceptions import ObjectDoesNotExist
import json
from django.utils import timezone


from websockets.models import Staff_Chat_Room, Staff_Room_Chat_Message
from websockets.models import Websocket_Error, Staff_Chat_Error


from websockets.staff_chat_constants import *
from websockets.exceptions import ClientError
from websockets.utils import calculate_timestamp, calculate_date_time
from websockets.serializers import LazyStaffRoomChatMessageEncoder, LazyStaffEncoder
from users.models import CustomUser
from site_admin.models import Room

# Example taken from:
# https://github.com/andrewgodwin/channels-examples/blob/master/multichat/chat/consumers.py
class StaffChatConsumer(AsyncJsonWebsocketConsumer):

	async def connect(self):
		"""
		Called when the websocket is handshaking as part of initial connection.
		"""
		print("\n\n\n*****StaffChatConsumer: connect: " + str(self.scope["user"]))
		# let everyone connect. But limit read/write to authenticated users
		try:
			await self.accept()
			self.room_id = None
		except Exception as e:
			socket_info={}
			socket_info['file']="consumer_staff_chat.py"
			socket_info['function_name']="connect"
			socket_info['location_in_function']="try block connecting"
			socket_info['occurred_for_user']=str(self.scope["user"])
			socket_info['error_text']=str(e)
			await create_log_of_error(socket_info)
		
		

	async def disconnect(self, code):
		"""
		Called when the WebSocket closes for any reason.
		"""
		# leave the room
		# print("StaffChatConsumer: disconnect")
		try:
			if self.room_id != None:
				await self.leave_room(self.room_id)
		except Exception as e:
			socket_info={}
			socket_info['file']="consumer_staff_chat.py"
			socket_info['function_name']="disconnect"
			socket_info['location_in_function']="try block disconnecting"
			socket_info['occurred_for_user']=str(self.scope["user"])
			socket_info['error_text']=str(e)
			await create_log_of_error(socket_info)


	async def receive_json(self, content):
		"""
		Called when we get a text frame. Channels will JSON-decode the payload
		for us and pass it as the first argument.
		"""
		# Messages will have a "command" key we can switch on
		command = content.get("command", None)
		print("StaffChatConsumer: receive_json: " + str(command))
		print(content)
		try:
			if command == "send":
				try:
					if len(content["message"].lstrip()) != 0:
						await self.send_room(content["room_id"], content["message"], content['meeting_room'], content['meeting_room_id'])
					# raise ClientError(422,"You can't send an empty message.")
				except Exception as e:
					socket_info={}
					socket_info['file']="consumer_staff_chat.py"
					socket_info['function_name']="receive_json"
					socket_info['location_in_function']="command send"
					socket_info['occurred_for_user']=str(self.scope["user"])
					socket_info['error_text']=str(e)
					await create_log_of_error(socket_info)			
				
			elif command == "join_staff":
				try:
					# Make them join the room
					await self.join_room(content["room"])
				except Exception as e:
					socket_info={}
					socket_info['file']="consumer_staff_chat.py"
					socket_info['function_name']="receive_json"
					socket_info['location_in_function']="command join_staff"
					socket_info['occurred_for_user']=str(self.scope["user"])
					socket_info['error_text']=str(e)
					await create_log_of_error(socket_info)	

				
			elif command == "leave":
				
				try:
					# Leave the room
					await self.leave_room(content["room"])
				except Exception as e:
					socket_info={}
					socket_info['file']="consumer_staff_chat.py"
					socket_info['function_name']="receive_json"
					socket_info['location_in_function']="command leave"
					socket_info['occurred_for_user']=str(self.scope["user"])
					socket_info['error_text']=str(e)
					await create_log_of_error(socket_info)

			elif command == "get_room_chat_messages":
				try:
					await self.display_progress_bar(True)
					room = await get_room_or_error(content['room_id'])
					payload = await get_room_chat_messages(room, content['page_number'])
					unread_counts = await get_unread_counts()
					if payload != None:
						payload = json.loads(payload)
						await self.send_messages_payload(payload['messages'],
										payload['new_page_number'], unread_counts)
					else:
						socket_info={}
						socket_info['file']="consumer_staff_chat.py"
						socket_info['function_name']="receive_json"
						socket_info['location_in_function']="command get_room_chat_messages"
						socket_info['occurred_for_user']=str(self.scope["user"])
						socket_info['error_text']="Something went wrong retrieving the chatroom messages."
						await create_log_of_error(socket_info)
						raise ClientError(204,"Something went wrong retrieving the chatroom messages.")
					await self.display_progress_bar(False)

				except Exception as e:
					socket_info={}
					socket_info['file']="consumer_staff_chat.py"
					socket_info['function_name']="receive_json"
					socket_info['location_in_function']="command get_room_chat_messages"
					socket_info['occurred_for_user']=str(self.scope["user"])
					socket_info['error_text']=str(e)
					await create_log_of_error(socket_info)
			
				
		except ClientError as e:
			socket_info={}
			socket_info['file']="consumer_staff_chat.py"
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
		# print("StaffChatConsumer: send_room")

		try:
			if self.room_id != None:
				if str(room_id) != str(self.room_id):
					socket_info={}
					socket_info['file']="consumer_staff_chat.py"
					socket_info['function_name']="send_room"
					socket_info['location_in_function']="if str(room_id) != str(self.room_id):"
					socket_info['occurred_for_user']=str(self.scope["user"])
					socket_info['error_text']="str(room_id) = " + str(room_id) + " str(self.room_id) = " + str(self.room_id)
					await create_log_of_error(socket_info)
					raise ClientError("ROOM_ACCESS_DENIED", "Staff Room access denied")

				if not is_authenticated(self.scope["user"]):
					socket_info={}
					socket_info['file']="consumer_staff_chat.py"
					socket_info['function_name']="send_room"
					socket_info['location_in_function']="if not is_authenticated(self.scope['user']):"
					socket_info['occurred_for_user']=str(self.scope["user"])
					socket_info['error_text']="not authenticated"
					await create_log_of_error(socket_info)
					raise ClientError("ROOM_ACCESS_DENIED", "Staff Room access denied")
					raise ClientError("AUTH_ERROR", "Staff Room: You must be authenticated to chat.")
			else:
				socket_info={}
				socket_info['file']="consumer_staff_chat.py"
				socket_info['function_name']="send_room"
				socket_info['location_in_function']="else of -- if self.room_id != None:"
				socket_info['occurred_for_user']=str(self.scope["user"])
				socket_info['error_text']=str(e)
				await create_log_of_error(socket_info)
				raise ClientError("ROOM_ACCESS_DENIED", "Staff Room access denied")

			# Get the room and send to the group about it
			try:
				room = await get_room_or_error(room_id)
				await create_staff_room_chat_message(room, self.scope["user"], message, meeting_room, meeting_room_id)
				unread_counts = await get_unread_counts()

				await self.channel_layer.group_send(
					room.group_name,
					{
						"type": "chat.message",
						# "profile_image": self.scope["user"].profile_image.url,
						"username": self.scope["user"].username,
						"user_id": self.scope["user"].id,
						"message": message,
						"meeting_room_name": meeting_room,
						"unread_counts": unread_counts,
					}
				)
			except Exception as e:
				socket_info={}
				socket_info['file']="consumer_staff_chat.py"
				socket_info['function_name']="send_room"
				socket_info['location_in_function']="Get the room and send to the group about it"
				socket_info['occurred_for_user']=str(self.scope["user"])
				socket_info['error_text']=str(e)
				await create_log_of_error(socket_info)

			
		except Exception as e:
			socket_info={}
			socket_info['file']="consumer_staff_chat.py"
			socket_info['function_name']="send_room"
			socket_info['location_in_function']="try block send_room"
			socket_info['occurred_for_user']=str(self.scope["user"])
			socket_info['error_text']=str(e)
			await create_log_of_error(socket_info)
	
		

	async def chat_message(self, event):
		"""
		Called when someone has messaged our chat.
		"""
		# Send a message down to the client
		# print("StaffChatConsumer: chat_message from user #" + str(event["user_id"]))
		timestamp = calculate_timestamp(timezone.localtime(timezone.now()))
		try:
			await self.send_json(
				{
					"msg_type": STAFF_MSG_TYPE_MESSAGE,
					# "profile_image": event["profile_image"],
					"username": event["username"],
					"user_id": event["user_id"],
					"message": event["message"],
					"meeting_room_name": event["meeting_room_name"],
					"natural_timestamp": timestamp,
					"staff_msg_counts": event["unread_counts"],
				},
			)
		except Exception as e:
			socket_info={}
			socket_info['file']="consumer_staff_chat.py"
			socket_info['function_name']="async def chat_message"
			socket_info['location_in_function']="async def chat_message"
			socket_info['occurred_for_user']=str(self.scope["user"])
			socket_info['error_text']=str(e)
			await create_log_of_error(socket_info)
	
		

	async def join_room(self, room_id):
		"""
		Called by receive_json when someone sent a join command.
		"""
		# print("StaffChatConsumer: join_room")
		is_auth = is_authenticated(self.scope["user"])
		# print("is_auth", is_auth)
		try:
			room = await get_room_or_error(room_id)
			# print("room", room)
		except ClientError as e:
			socket_info={}
			socket_info['file']="consumer_staff_chat.py"
			socket_info['function_name']="async def join_room"
			socket_info['location_in_function']="async def join_room"
			socket_info['occurred_for_user']=str(self.scope["user"])
			socket_info['error_text']=str(e)
			await create_log_of_error(socket_info)
			await self.handle_client_error(e)

		# Add user to "users" list for room
		try:
			if is_auth:
				await connect_user(room, self.scope["user"])

			# Store that we're in the room
			self.room_id = room.id

			# print("Self.room_id", self.room_id)

			# Add them to the group so they get room messages
			await self.channel_layer.group_add(
				room.group_name,
				self.channel_name,
			)

			# Instruct their client to finish opening the room
			await self.send_json({
				"join": str(room.id)
			})

			# send the new user count to the room
			num_connected_users = await get_num_connected_users(room)
			await self.channel_layer.group_send(
				room.group_name,
				{
					"type": "connected.user.count",
					"connected_user_count": num_connected_users,
				}
			)
		except Exception as e:
			socket_info={}
			socket_info['file']="consumer_staff_chat.py"
			socket_info['function_name']="async def join_room 2"
			socket_info['location_in_function']="async def join_room 2"
			socket_info['occurred_for_user']=str(self.scope["user"])
			socket_info['error_text']=str(e)
			await create_log_of_error(socket_info)



	async def leave_room(self, room_id):
		"""
		Called by receive_json when someone sent a leave command.
		"""
		# print("StaffChatConsumer: leave_room")
		try:
			is_auth = is_authenticated(self.scope["user"])
			room = await get_room_or_error(room_id)

			# Remove user from "users" list
			if is_auth:
				await disconnect_user(room, self.scope["user"])

			# Remove that we're in the room
			self.room_id = None
			# Remove them from the group so they no longer get room messages
			await self.channel_layer.group_discard(
				room.group_name,
				self.channel_name,
			)

			# send the new user count to the room
			num_connected_users = await get_num_connected_users(room)
			await self.channel_layer.group_send(
			room.group_name,
				{
					"type": "connected.user.count",
					"connected_user_count": num_connected_users,
				}
			)
		except Exception as e:
			socket_info={}
			socket_info['file']="consumer_staff_chat.py"
			socket_info['function_name']="async def leave_room"
			socket_info['location_in_function']="async def leave_room"
			socket_info['occurred_for_user']=str(self.scope["user"])
			socket_info['error_text']=str(e)
			await create_log_of_error(socket_info)
		

	async def handle_client_error(self, e):
		"""
		Called when a ClientError is raised.
		Sends error data to UI.
		"""
		try:
			errorData = {}
			errorData['error'] = e.code
			if e.message:
				errorData['message'] = e.message
				await self.send_json(errorData)
		except Exception as e:
			socket_info={}
			socket_info['file']="consumer_staff_chat.py"
			socket_info['function_name']="async def handle_client_error(self, e):"
			socket_info['location_in_function']="async def handle_client_error(self, e):"
			socket_info['occurred_for_user']=str(self.scope["user"])
			socket_info['error_text']=str(e)
			await create_log_of_error(socket_info)

		return

	async def send_messages_payload(self, messages, new_page_number, unread_counts):
		"""
		Send a payload of messages to the ui
		"""
		# print("StaffChatConsumer: send_messages_payload. ")
		try:
			await self.send_json(
				{
					"messages_payload": "messages_payload",
					"messages": messages,
					"new_page_number": new_page_number,
					"unread_counts": unread_counts,
				},
			)
		except Exception as e:
			socket_info={}
			socket_info['file']="consumer_staff_chat.py"
			socket_info['function_name']="async def send_messages_payload"
			socket_info['location_in_function']="async def send_messages_payload"
			socket_info['occurred_for_user']=str(self.scope["user"])
			socket_info['error_text']=str(e)
			await create_log_of_error(socket_info)
		

		

	async def connected_user_count(self, event):
		"""
		Called to send the number of connected users to the room.
		This number is displayed in the room so other users know how many users are connected to the chat.
		"""
		# Send a message down to the client
		# print("StaffChatConsumer: connected_user_count: count: " + str(event["connected_user_count"]))
		try:
			await self.send_json(
				{
					"msg_type": STAFF_MSG_TYPE_CONNECTED_USER_COUNT,
					"connected_user_count": event["connected_user_count"]
				},
			)
		except Exception as e:
			socket_info={}
			socket_info['file']="consumer_staff_chat.py"
			socket_info['function_name']="async def connected_user_count"
			socket_info['location_in_function']="async def connected_user_count"
			socket_info['occurred_for_user']=str(self.scope["user"])
			socket_info['error_text']=str(e)
			await create_log_of_error(socket_info)

		

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
def get_num_connected_users(room):
	try:
		# room = Chat_Room.objects.get(pk=room_id)
		count= len(room.users.all())
		print("room", room, type(room))
		print("count", count)	
	except Exception as e:
		print("\n\n\nBROKEN get_user_count_in_room")

		socket_info={}
		socket_info['file']="consumer_staff_chat.py"
		socket_info['function_name']="database_sync_to_async get_num_connected_users"
		socket_info['location_in_function']="database_sync_to_async get_num_connected_users"
		socket_info['occurred_for_user']=str(self.scope["user"])
		socket_info['error_text']=str(e)
		Staff_Chat_Error.objects.create(file=socket_info['file'],
						function_name=socket_info['function_name'],
						location_in_function=socket_info['location_in_function'],
						occurred_for_user=socket_info['occurred_for_user'],
						error_text=socket_info['error_text'])
	
		
	return count

@database_sync_to_async
def create_staff_room_chat_message(room, user, message, meeting_room, meeting_room_id):
	print("\n\n\n\n###########Meeting Room", meeting_room_id)


	try:
		page = Room.objects.get(id=meeting_room_id)
		all_staff = CustomUser.objects.filter(role__name = "Staff").exclude(id=user.id)
		for member in all_staff:
			member.unread_staff.add_one()

		message = Staff_Room_Chat_Message.objects.create(user=user, room=room,
						meeting_room= page, content=message)

	# all_staff_counts = CustomUser.objects.filter(role__name = "Staff")
	# payload = {}
	# s = LazyStaffEncoder()
	# payload['all_staff_counts'] = s.serialize(all_staff_counts)
	# data = json.dumps(payload)
	except Exception as e:
		socket_info={}
		socket_info['file']="consumer_staff_chat.py"
		socket_info['function_name']="database_sync_to_async create_staff_room_chat_message"
		socket_info['location_in_function']="database_sync_to_async create_staff_room_chat_message"
		socket_info['occurred_for_user']=str(self.scope["user"])
		socket_info['error_text']=str(e)
		Staff_Chat_Error.objects.create(file=socket_info['file'],
						function_name=socket_info['function_name'],
						location_in_function=socket_info['location_in_function'],
						occurred_for_user=socket_info['occurred_for_user'],
						error_text=socket_info['error_text'])
	
	return message

@database_sync_to_async
def get_unread_counts():
	try:
		all_staff_counts = CustomUser.objects.filter(role__name = "Staff")
		payload = {}
		s = LazyStaffEncoder()
		payload['all_staff_counts'] = s.serialize(all_staff_counts)
		data = json.dumps(payload)
	except Exception as e:
		socket_info={}
		socket_info['file']="consumer_staff_chat.py"
		socket_info['function_name']="database_sync_to_async get_unread_counts"
		socket_info['location_in_function']="database_sync_to_async get_unread_counts"
		socket_info['occurred_for_user']=str(self.scope["user"])
		socket_info['error_text']=str(e)
		Staff_Chat_Error.objects.create(file=socket_info['file'],
						function_name=socket_info['function_name'],
						location_in_function=socket_info['location_in_function'],
						occurred_for_user=socket_info['occurred_for_user'],
						error_text=socket_info['error_text'])


	
	return data

@database_sync_to_async
def connect_user(room, user):
	# print("Connect User", room, user)
	return room.connect_user(user)

@database_sync_to_async
def disconnect_user(room, user):
    return room.disconnect_user(user)

@database_sync_to_async
def get_room_or_error(room_id):
	print("Get Room or Error", room_id)

	try:
		room = Staff_Chat_Room.objects.get(pk=room_id)

	except Exception as e:

		print("\n\n\nBROKEN Staff Chat get_room_or_error", e)
		socket_info={}
		socket_info['file']="consumer_staff_chat.py"
		socket_info['function_name']="database_sync_to_async get_room_or_error"
		socket_info['location_in_function']="database_sync_to_async get_room_or_error"
		socket_info['occurred_for_user']=str(self.scope["user"])
		socket_info['error_text']=str(e)
		Staff_Chat_Error.objects.create(file=socket_info['file'],
						function_name=socket_info['function_name'],
						location_in_function=socket_info['location_in_function'],
						occurred_for_user=socket_info['occurred_for_user'],
						error_text=socket_info['error_text'])
		
	return room



@database_sync_to_async
def get_room_chat_messages(room, page_number):
	try:
		qs = Staff_Room_Chat_Message.objects.by_room(room)
		p = Paginator(qs, STAFF_DEFAULT_ROOM_CHAT_MESSAGE_PAGE_SIZE)

		payload = {}
		messages_data = None
		new_page_number = int(page_number)  
		if new_page_number <= p.num_pages:
			new_page_number = new_page_number + 1
			s = LazyStaffRoomChatMessageEncoder()
			payload['messages'] = s.serialize(p.page(page_number).object_list)
		else:
			payload['messages'] = "None"
		payload['new_page_number'] = new_page_number
		return json.dumps(payload)
	except Exception as e:
		print("EXCEPTION: " + str(e))
		socket_info={}
		socket_info['file']="consumer_staff_chat.py"
		socket_info['function_name']="database_sync_to_async get_room_chat_messages"
		socket_info['location_in_function']="database_sync_to_async get_room_chat_messages"
		socket_info['occurred_for_user']=str(self.scope["user"])
		socket_info['error_text']=str(e)
		Staff_Chat_Error.objects.create(file=socket_info['file'],
						function_name=socket_info['function_name'],
						location_in_function=socket_info['location_in_function'],
						occurred_for_user=socket_info['occurred_for_user'],
						error_text=socket_info['error_text'])
		return None

@database_sync_to_async
def create_log_of_error(socket_info):
	try:
		Staff_Chat_Error.objects.create(file=socket_info['file'],
						function_name=socket_info['function_name'],
						location_in_function=socket_info['location_in_function'],
						occurred_for_user=socket_info['occurred_for_user'],
						error_text=socket_info['error_text'])

	except Exception as e:
		print("\n\n\nBROKEN create_log_of_error")