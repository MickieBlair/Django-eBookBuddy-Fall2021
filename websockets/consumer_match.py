import json
import asyncio

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from asgiref.sync import async_to_sync
from django.utils import timezone

from channels.exceptions import StopConsumer

from websockets.database_sync_to_async_functions import *

class MatchConsumer(AsyncJsonWebsocketConsumer):
	async def connect(self):
		print("\n\n\nMatchConsumer: connect: " + str(self.scope["user"]))

		self.location_name = self.scope['url_route']['kwargs']['location_id']
		# print("\n1 MatchConsumer:", self.location_name)
		self.socket_group_name = 'match'

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
		print("\n*******************MatchConsumer: disconnect", timezone.now())

		try:
			self.room = await get_room_by_location(self.scope["user"], self.scope['url_route']['kwargs']['location_id'])
		
		except Exception as e:
			socket_info={}
			socket_info['file']="consumer_match.py"
			socket_info['function_name']="disconnect"
			socket_info['location_in_function']="setting self.room"
			socket_info['occurred_for_user']=str(self.scope["user"])
			socket_info['error_text']=str(e) 
			await create_log_of_error(socket_info)
		

		# print("testing", room)
		if self.room:
			print("Current", self.room)			
			try:
				await self.leave_room(self.room)
				print("\n\n\nDisconnecting Self", self.scope['url_route']['kwargs']['location_id'])
			except Exception as e:
				socket_info={}
				socket_info['file']="consumer_match.py"
				socket_info['function_name']="disconnect"
				socket_info['location_in_function']="try block disconnecting"
				socket_info['occurred_for_user']=str(self.scope["user"])
				socket_info['error_text']="Error: " + str(e) + "--Location: " + str(self.scope['url_route']['kwargs']['location_id'])
				await create_log_of_error(socket_info)
		else:
			try:
				self.room = await get_room_by_location(self.scope["user"], self.scope['url_route']['kwargs']['location_id'])
				if self.room:
					await self.leave_room(self.room)
				print("\n\n\nDisconnecting Self", self.scope['url_route']['kwargs']['location_id'])
			except Exception as e:
				socket_info={}
				socket_info['file']="consumer_match.py"
				socket_info['function_name']="disconnect"
				socket_info['location_in_function']="try block disconnecting 2"
				socket_info['occurred_for_user']=str(self.scope["user"])
				socket_info['error_text']="Error: " + str(e) + "didn't work"
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



	# async def disconnect(self, code):
	# 	# print("\n*******************MatchConsumer: disconnect", timezone.now(), self, code)
		
	# 	try:
	# 		self.room = await get_room_by_location(self.scope["user"], self.scope['url_route']['kwargs']['location_id'])
		
	# 	except Exception as e:
	# 		socket_info={}
	# 		socket_info['file']="consumer_match.py"
	# 		socket_info['function_name']="disconnect"
	# 		socket_info['location_in_function']="setting self.room"
	# 		socket_info['occurred_for_user']=str(self.scope["user"])
	# 		socket_info['error_text']=str(e) 
	# 		await create_log_of_error(socket_info)
		

	# 	# print("testing", room)
	# 	if self.room:
	# 		print("Current", self.room)			
	# 		try:
	# 			await self.leave_room(self.room)
	# 			print("\n\n\nDisconnecting Self", self.scope['url_route']['kwargs']['location_id'])
	# 		except Exception as e:
	# 			socket_info={}
	# 			socket_info['file']="consumer_match.py"
	# 			socket_info['function_name']="disconnect"
	# 			socket_info['location_in_function']="try block disconnecting"
	# 			socket_info['occurred_for_user']=str(self.scope["user"])
	# 			socket_info['error_text']="Error: " + str(e) + "--Location: " + str(self.scope['url_route']['kwargs']['location_id'])
	# 			await create_log_of_error(socket_info)
	# 	else:
	# 		try:
	# 			self.room = await get_room_by_location(self.scope["user"], self.scope['url_route']['kwargs']['location_id'])
	# 			if self.room:
	# 				await self.leave_room(self.room)
	# 			print("\n\n\nDisconnecting Self", self.scope['url_route']['kwargs']['location_id'])
	# 		except Exception as e:
	# 			socket_info={}
	# 			socket_info['file']="consumer_match.py"
	# 			socket_info['function_name']="disconnect"
	# 			socket_info['location_in_function']="try block disconnecting 2"
	# 			socket_info['occurred_for_user']=str(self.scope["user"])
	# 			socket_info['error_text']="Error: " + str(e) + "didn't work"
	# 			await create_log_of_error(socket_info)
			


	async def receive_json(self, content):
		command = content.get("command", None)
		# print("\n***** MatchConsumer: receive_json: " + str(self.scope["user"]))
		# print("This is the command", command)

		if command =="join":
			# print("\n\n\nJOIN", content)
			await self.join_room(content);

			# get private message count
			await self.get_unread_private_message_count(content)
			# await self.join_meeting_room()
			# await self.send_session_stats()

		elif command == "redirect_user":
			# print('\n\n\n\nredirect_user', content)
			redirect = await get_redirect_by_id(content['user_id'], content['redirect_id']);
			await self.send_redirect(redirect)

		elif command == "get_all_redirects":
			# print('\n\n\n\nget_all_redirects', content)
			all_redirects, redirect_count = await get_all_redirects(content['user_id']);

			await self.channel_layer.group_send(
					self.socket_group_name,
					{
						"type": "current_redirects",
						"all_redirects": all_redirects,
						"redirect_count": redirect_count
					}
				)

		elif command == "get_api_participants":
			print("\n\n\n\n*****get_api_participants")
			await self.channel_layer.group_send(
					self.socket_group_name,
					{
						"type": "get_api_participants",						
					}
				)


		elif command == "delete_redirect":
			# print('\n\n\n\ndelete_redirect', content)
			all_redirects, redirect_count = await delete_redirect_by_id(content['user_id'], content['redirect_id']);

			await self.channel_layer.group_send(
					self.socket_group_name,
					{
						"type": "current_redirects",
						"all_redirects": all_redirects,
						"redirect_count": redirect_count
					}
				)

				# await self.send_redirect(redirect)

		elif command == "manual_redirect":
				
			manual_redirects, manual_redirect_count = await create_manual_redirects(content)

			await self.channel_layer.group_send(
				self.socket_group_name,
				{
					"type": "redirect_users",
					"manual_redirects": manual_redirects,
					"manual_redirect_count": manual_redirect_count
				}
			)

			
		elif command == "create_temp_match":
				print("create_temp_match", content)
				redirect = await create_temporary_match(self.scope["user"], content)
				print("create_temp_match", redirect)
				if redirect:
					print("Create Temp Match Redirect ID", redirect.id)
					print("Create Temp Match user id", redirect.user_to_redirect.id)
					print("Create Temp Match to user id", redirect.to_user.id)
					print("Create Temp Match to room id", redirect.to_room.id)
					await self.user_send_redirect(redirect)

		elif command == "notify_all":
				# print("notify_all", content)
				if len(content["message"].lstrip()) != 0:
					await self.send_to_all_rooms(content)

		elif command == "help_request":
				# print("help_request", content)
				all_help_requests, help_count = await create_help_request(content)
				# new_help = await create_help_request(content)
				# all_help_requests, help_count = await get_help_requests(self.scope["user"])
				await self.channel_layer.group_send(
					self.socket_group_name,
					{
						"type": "help_requests",
						# "new_help": new_help,
						"all_help_requests": all_help_requests,
						"help_count": help_count
					}
				)

		elif command == "mark_help_request_done":
				# print("\n\n\n*********mark_help_request_done", content)
				status = await mark_help_request_done(self.scope["user"], content['request_id'])

				if content['send_to_staff']:
					# print("\n\n\n***NOW SEND*****")
					all_help_requests, help_count = await get_help_requests(self.scope["user"])
					await self.channel_layer.group_send(
						self.socket_group_name,
						{
							"type": "help_requests",
							"all_help_requests": all_help_requests,
							"help_count": help_count
						}
					)
				# else:
				# 	print("\n\n\n\nNot Sending Yet")

		

		elif command == "create_send_private_message":
				# print("******create_send_private_message", content)

				private_chat_room = await get_private_room_or_error(content['room_id'], self.scope["user"])
				# print(private_chat_room)
				await private_connect_user(private_chat_room, self.scope["user"])
				private_room_id = private_chat_room.id
				if len(content["pvt_message"].lstrip()) == 0:
					raise ClientError(422,"You can't send an empty message.")
				await self.send_room_join_send_leave(private_chat_room, self.scope["user"], content)
				await private_disconnect_user(private_chat_room, self.scope["user"])

		elif command == "get_private_rooms":
			# print("\n\n**** GETTING private_room_list", content)
			pvt_rooms, pvt_room_count = await get_private_rooms_for_user(content['user_id'])
			# print("get_private_rooms", pvt_rooms, pvt_room_count)
			await self.channel_layer.group_send(
				self.socket_group_name,
				{
					"type": "private_room_list",
					"for_user": content['user_id'],
					"pvt_rooms": pvt_rooms,
					"pvt_room_count": pvt_room_count,
				}
			)

		elif command == "get_private_messages":
			# print("\n\n**** GETTING Private Messages", content)
			user_private_unread = await to_user_unread_count(content['user_id'])
			unread_by_user = await unread_private_msg_by_user(content['user_id'])
			await self.channel_layer.group_send(
				self.socket_group_name,
				{
					"type": "unread_private_messages",
					"for_user": content['user_id'],
					"pvt_unread_count": user_private_unread,
					"unread_by_room_total": unread_by_user,
				}
			)
			
		# elif command == "user_leaving":
			
		elif command == "send_session_stats":
			print("***Sending Session stats")
			await self.send_session_stats()


	async def send_redirect(self, redirect):
		link_id = "get_room_link-" + str(redirect['to_room_id'])
		await self.channel_layer.group_send(
			self.socket_group_name,
			{
				'type': 'redirect_user',
				"redirect_user_id": redirect['user_to_redirect_id'],
				"to_room_id": redirect['to_room_id'],
				"link_id": link_id,
			}
		)

	async def user_send_redirect(self, redirect):

		link_id = "get_room_link-" + str(redirect.to_room.id)
		print("get_room_link-", link_id)
		await self.channel_layer.group_send(
			self.socket_group_name,
			{
				'type': 'redirect_user',
				"redirect_user_id": redirect.user_to_redirect.id,
				"to_room_id": redirect.to_room.id,
				"link_id": link_id,
			}
		)

	async def redirect_user(self, event):		
		await self.send_json(
			{
				"msg_type": "redirect_user",				
				"redirect_user_id": event['redirect_user_id'],
				"to_room_id": event['to_room_id'],
				"link_id": event['link_id'],
			},
		)

	async def get_api_participants(self, event):
		await self.send_json(
			{
				"msg_type": "get_api_participants",
			},
		)

	async def current_redirects(self, event):
		await self.send_json(
			{
				"msg_type": "current_redirects",
				"all_redirects": event["all_redirects"],
				"redirect_count": event["redirect_count"]
			},
		)

	async def help_requests(self, event):
		await self.send_json(
			{
				"msg_type": "help_requests",
				"all_help_requests": event["all_help_requests"],
				"help_count": event["help_count"]
			},
		)

	async def redirect_users(self, event):
		# print("new_redirect" + str(event["new_redirect"]))
		# print("all redirect " + str(event["student_redirects"]))
		await self.send_json(
			{
				"msg_type": "manual_redirects",
				"manual_redirects": event["manual_redirects"],
				"manual_redirect_count": event["manual_redirect_count"]
			},
		)

	async def send_session_stats(self):
		session_stats = await get_session_stats(self.scope["user"])

		await self.channel_layer.group_send(
			self.socket_group_name,
			{
				"type": "session_stats",
				"session_stats": session_stats,					
			}
		)

	async def session_stats(self, event):
		await self.send_json(
			{
				"msg_type": "session_stats",
				"session_stats": event["session_stats"],				
			},
		)


	async def join_room(self, content):
		# print("JOIN ROOM", content)
		room_id = content['room_id']
		try:
			self.user, self.role = await get_user_or_error(str(self.scope["user"]))
			await adjust_socket_group_participants(self.scope['user'], self.socket_group_name, True)
			self.room, redirect = await adjust_user_session_status(self.user, self.role, room_id, True)
			if redirect:
				if redirect == "Kick":
					print("NOT SUPPOSED TO BE HERE")
					await self.channel_layer.group_send(
						self.socket_group_name,
						{
							"type": "student_not_scheduled",
							"student_out_id": self.user.id,					
						}
					)
				else:
					print("JOIN ROOM",self.room, self.scope['user'], redirect)
					await self.user_send_redirect(redirect)
			else:
				print("JOIN ROOM NO REDIRECT",self.room, self.scope['user'], redirect)

			# print("\nMatchConsumer: self.room", self.user, self.room)
		except Exception as e:
			print("Connect, getting user and role", e)
			socket_info={}
			socket_info['file']="match_consumer.py"
			socket_info['function_name']="connect 1"
			socket_info['location_in_function']="try block for getting user and role"
			socket_info['occurred_for_user']=str(self.scope["user"])
			socket_info['error_text']=e
			await create_log_of_error(socket_info)

		try:
			await self.join_meeting_room()

			session_stats = await get_session_stats(self.scope["user"])

			await self.channel_layer.group_send(
				self.socket_group_name,
				{
					"type": "session_stats",
					"session_stats": session_stats,					
				}
			)

		except Exception as e:
			print("Broken joining session stats", e)
			socket_info={}
			socket_info['file']="match_consumer.py"
			socket_info['function_name']="join_room"
			socket_info['location_in_function']="try block session_stats"
			socket_info['occurred_for_user']=str(self.scope["user"])
			socket_info['error_text']=e
			await create_log_of_error(socket_info)

	async def get_unread_private_message_count(self,content):
		try:
			user_private_unread = await to_user_unread_count(self.user.id)
			unread_by_user = await unread_private_msg_by_user(self.user.id)
			await self.channel_layer.group_send(
				self.socket_group_name,
				{
					"type": "unread_private_messages",
					"for_user": self.user.id,
					"pvt_unread_count": user_private_unread,
					"unread_by_room_total": unread_by_user,
				}
			)

		except Exception as e:
			print("Broken joining private_messages", e)
			socket_info={}
			socket_info['file']="match_consumer.py"
			socket_info['function_name']="join_room"
			socket_info['location_in_function']="try block getting private messages"
			socket_info['occurred_for_user']=str(self.scope["user"])
			socket_info['error_text']=e
			await create_log_of_error(socket_info)


	async def join_meeting_room(self):
		await self.channel_layer.group_send(
			self.socket_group_name,
			{
				'type': 'member_joining',
				"full_name": self.scope["user"].full_name,
				"username": self.scope["user"].username,
				"member_id": self.scope["user"].id,
				"role": self.role,
				"room_id": self.room.id,
				"room_name": self.room.name,
				"room_slug": self.room.slug,
				"room_row": "room_" + str(self.room.id),
				"room_count": self.room.num_participants,
			}
		)

	async def member_joining(self, event):		
		await self.send_json(
			{
				"msg_type": "member_joining",
				"full_name": event["full_name"],				
				"username": event["username"],
				"member_id": event["member_id"],
				"role": event["role"],
				"room_id": event["room_id"],
				"room_name": event["room_name"],
				"room_slug": event["room_slug"],
				"room_row": event["room_row"],
				"room_count": event["room_count"],
			},
		)

	


	async def leave_room(self, room):
		try:
			await adjust_socket_group_participants(self.scope['user'], self.socket_group_name, False)
			self.room, redirect = await adjust_user_session_status(self.user, self.role, room.id, False)
			if redirect:
				print("LEAVE ROOM", self.room, self.scope['user'] , redirect)
				await self.user_send_redirect(redirect)
			else:
				print("LEAVE ROOM NO REDIRECT",self.room, self.scope['user'], redirect)

			await delete_redirects_to_user(self.scope['user'])

			if self.role== "Volunteer" or self.role== "Staff":
				manual_redirects, manual_redirect_count = await check_for_students(self.user, self.role, room.id)
				if manual_redirect_count > 0:		
					await self.channel_layer.group_send(
						self.socket_group_name,
						{
							"type": "redirect_users",
							"manual_redirects": manual_redirects,
							"manual_redirect_count": manual_redirect_count
						}
					)

		except Exception as e:
			print("Exception Leaving, ", e)
			socket_info={}
			socket_info['file']="match_consumer.py"
			socket_info['function_name']="leave room"
			socket_info['location_in_function']="try block for leaving room"
			socket_info['occurred_for_user']=str(self.scope["user"])
			socket_info['error_text']=e
			await create_log_of_error(socket_info)

		try:
			# print("\n\n\n********LEAVING", self.user)
			await self.leave_meeting_room()
			# await self.send_session_stats()	
			session_stats = await get_session_stats(self.scope["user"])
			await self.channel_layer.group_send(
				self.socket_group_name,
				{
					"type": "session_stats",
					"session_stats": session_stats,				
				}
			)

		except Exception as e:
			print("Broken joining", e)
			socket_info={}
			socket_info['file']="match_consumer.py"
			socket_info['function_name']="join_room"
			socket_info['location_in_function']="try block sending json"
			socket_info['occurred_for_user']=str(self.scope["user"])
			socket_info['error_text']=e
			await create_log_of_error(socket_info)

	async def leave_meeting_room(self):
		# room_data = await get_rooms_and_participants(self.user)
		await self.channel_layer.group_send(
			self.socket_group_name,
			{
				'type': 'member_leaving',
				"full_name": self.scope["user"].full_name,
				"username": self.scope["user"].username,
				"member_id": self.scope["user"].id,
				"role": self.role,
				"room_id": self.room.id,
				"room_name": self.room.name,
				"room_slug": self.room.slug,
				"room_row": "room_" + str(self.room.id),
				"room_count": self.room.num_participants,
			}
		)



	async def member_leaving(self, event):		
		await self.send_json(
			{
				"msg_type": "member_leaving",
				"full_name": event["full_name"],				
				"username": event["username"],
				"member_id": event["member_id"],
				"role": event["role"],
				"room_id": event["room_id"],
				"room_name": event["room_name"],
				"room_slug": event["room_slug"],
				"room_row": event["room_row"],
				"room_count": event["room_count"],
			},
		)


	async def send_to_all_rooms(self, content):
		await self.channel_layer.group_send(
			self.socket_group_name,
			{
				'type': 'notify_all',
				"from": content['user_id'],
				'message': content['message'],
				"to_group": content['to_group']
			}
		)

	async def notify_all(self, event):
		await self.send_json(
			{
				"msg_type": "notify_all",
				"from": event['from'],
				'message': event['message'],
				"to_group": event['to_group'],
			},
		)
















	async def send_room_join_send_leave(self, room, user, content):
		"""
		Called by receive_json when someone sends a message to a room.
		"""
		# print("Match: Private Message send_room_join_send_leave")

		# get list of connected_users
		connected_users, user1, user2 = await private_get_connected_users(room)

		message = await create_private_chat_room_message(room, self.scope["user"], content)

		# Execute these functions asychronously
		await asyncio.gather(*[
			append_unread_msg_if_not_connected(self.scope["user"], room, user1, connected_users, message), 
			append_unread_msg_if_not_connected(self.scope["user"], room, user2, connected_users, message),

		])

		to_user_private_unread = await to_user_unread_count(content['to_user'])
		unread_by_user = await unread_private_msg_by_user(content['to_user'])
		# print("***********to_user_private_unread", to_user_private_unread)

		await self.channel_layer.group_send(
			self.socket_group_name,
			{
				"type": "private_message",
				"private_room_id": room.id,
				"to_user": message.to_user.id,
				"total_unread": to_user_private_unread,
				"unread_by_room_total": unread_by_user,
			}
		)


	async def private_message(self, event):
		"""
		Called when someone has messaged our chat.
		"""
		# Send a message down to the client
		# print("Match: private_chat_message")

		# timestamp = calculate_timestamp(timezone.now())

		await self.send_json(
			{
				"msg_type": "new_private_message",
				"in_private_room_id": event["private_room_id"],
				"to_user": event["to_user"],
				"total_unread": event["total_unread"],
				"unread_by_room_total": event["unread_by_room_total"],
			},
		)

	async def student_not_scheduled(self, event):
		await self.send_json(
			{
				"msg_type": "student_not_scheduled",
				"student_out_id": event["student_out_id"],
				
			},
		)


	async def private_room_list(self, event):
		await self.send_json(
			{
				"msg_type": "private_room_list",
				"for_user": event["for_user"],
				"pvt_rooms": event["pvt_rooms"],
				"pvt_room_count": event["pvt_room_count"],
			},
		)

	async def unread_private_messages(self, event):
		await self.send_json(
			{
				"msg_type": "unread_private_messages",
				"for_user": event["for_user"],
				"pvt_unread_count": event["pvt_unread_count"],
				"unread_by_room_total": event["unread_by_room_total"],
			},
		)




		

