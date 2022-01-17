from channels.db import database_sync_to_async
from django.core import serializers
from django.core.serializers import serialize
import json
from django.db.models import Q
from django.utils import timezone
from users.models import CustomUser
from jitsi_data.models import *
from jitsi_data.serializers import *
from site_admin.models import Room

@database_sync_to_async
def create_log_of_error(socket_info):
	try:
		Websocket_Error.objects.create(file=socket_info['file'],
						function_name=socket_info['function_name'],
						location_in_function=socket_info['location_in_function'],
						occurred_for_user=socket_info['occurred_for_user'],
						error_text=socket_info['error_text'])

	except Exception as e:
		print("\n\n\nBROKEN create_log_of_error Jitsi_Websocket_Error", e)

@database_sync_to_async
def get_user(user_id):
    try:
        return CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
    	Jitsi_Websocket_Error.objects.create(file="jitsi_database_asynce.py",
						function_name="get_user(user_id)",
						location_in_function="getting the user",
						occurred_for_user="user_id" + str(user_id),
						error_text=str("CustomUser.DoesNotExist"))
    	return None


@database_sync_to_async
def join_set_room_and_jitsi_status(user, jitsi_id, member_id, display_name,
									jitsi_room, room_name):
	data = ""
	print("\n\nJoining", room_name)
	try:
		room = Room.objects.get(name = room_name)
		jitsi_status, created = Jitsi_User_Status.objects.get_or_create(user = user)
		jitsi_status.jitsi_id = jitsi_id
		jitsi_status.online = True
		jitsi_status.room = room
		jitsi_status.save()
		j_room, created = Jitsi_Meeting_Room.objects.get_or_create(room = room)
		j_room.add_participant(user)
		j_room.check_student_alone_mismatch()
		payload={}

		# try:
		# 	s1 = LazyJitsiUserStatusEncoder()
		# 	payload['user_jitsi_status'] = s1.serialize([user])
		# except Exception as e:
		# 	print("EXCEPTION LazyJitsiUserStatusEncoder", e)
		# 	Jitsi_Websocket_Error.objects.create(file="jitsi_database_asynce.py",
		# 				function_name="join_set_room_and_jitsi_status",
		# 				location_in_function="LazyJitsiUserStatusEncoder",
		# 				occurred_for_user=str(user.username),
		# 				error_text=str(e))

		try:
			s2 = LazyJitsiRoomAndParticipantsEncoder()
			payload['jitsi_room_data'] = s2.serialize([j_room])
		except Exception as e:
			print("EXCEPTION LazyJitsiRoomAndParticipantsEncoder", e)
			Jitsi_Websocket_Error.objects.create(file="jitsi_database_asynce.py",
						function_name="join_set_room_and_jitsi_status",
						location_in_function="LazyJitsiRoomAndParticipantsEncoder",
						occurred_for_user=str(user.username),
						error_text=str(e))
		
		
		data = json.dumps(payload)
		

	except Exception as e:
		print("EXCEPTION join_set_room_and_jitsi_status", e)
		Jitsi_Websocket_Error.objects.create(file="jitsi_database_asynce.py",
						function_name="join_set_room_and_jitsi_status",
						location_in_function="overall try",
						occurred_for_user=str(user.username),
						error_text=str(e) + " - " +str(room_name))

	return data

@database_sync_to_async
def leave_set_room_and_jitsi_status(user, jitsi_id, member_id, display_name, 
									jitsi_room, room_name):
	data=''
	print("\n\nLeaving", room_name)
	try:
		room = Room.objects.get(name = room_name)
		jitsi_status, created = Jitsi_User_Status.objects.get_or_create(user = user)
		jitsi_status.jitsi_id = None
		jitsi_status.online = False
		jitsi_status.room = None
		jitsi_status.save()
		j_room, created = Jitsi_Meeting_Room.objects.get_or_create(room = room)
		j_room.remove_participant(user)
		j_room.check_student_alone_mismatch()
		payload={}

		# try:
		# 	s1 = LazyJitsiUserStatusEncoder()
		# 	payload['user_jitsi_status'] = s1.serialize([user])
		# except Exception as e:
		# 	print("EXCEPTION LazyJitsiUserStatusEncoder", e)
		# 	Jitsi_Websocket_Error.objects.create(file="jitsi_database_asynce.py",
		# 				function_name="leave_set_room_and_jitsi_status",
		# 				location_in_function="LazyJitsiUserStatusEncoder",
		# 				occurred_for_user=str(user.username),
		# 				error_text=str(e))

		try:
			s2 = LazyJitsiRoomAndParticipantsEncoder()
			payload['jitsi_room_data'] = s2.serialize([j_room])
		except Exception as e:
			print("EXCEPTION LazyJitsiRoomAndParticipantsEncoder", e)
			Jitsi_Websocket_Error.objects.create(file="jitsi_database_asynce.py",
						function_name="leave_set_room_and_jitsi_status",
						location_in_function="LazyJitsiRoomAndParticipantsEncoder",
						occurred_for_user=str(user.username),
						error_text=str(e))
		
		
		data = json.dumps(payload)
		

	except Exception as e:
		print("EXCEPTION leave_set_room_and_jitsi_status", e)
		Jitsi_Websocket_Error.objects.create(file="jitsi_database_asynce.py",
						function_name="leave_set_room_and_jitsi_status",
						location_in_function="overall try",
						occurred_for_user=str(user.username),
						error_text=str(e)  + " - " +str(room_name))

	return data


@database_sync_to_async
def disconnect_set_room_and_jitsi_status(user_ini, room_name):
	print("\n\nDisconnecting Jitsi", user_ini, room_name)

	try:
		user = CustomUser.objects.get(id=user_ini.id)
		jitsi_status, created = Jitsi_User_Status.objects.get_or_create(user = user)
		if jitsi_status.room:
			send_data = True			
			jitsi_status.jitsi_id = None
			jitsi_status.online = False
			jitsi_status.room = None
			jitsi_status.save()
			room = Room.objects.get(name=room_name)
			j_room, created = Jitsi_Meeting_Room.objects.get_or_create(room = room)
			j_room.remove_participant(user)
			j_room.check_student_alone_mismatch()
			payload={}
			# try:
			# 	s1 = LazyJitsiUserStatusEncoder()
			# 	payload['user_jitsi_status'] = s1.serialize([user])
			# except Exception as e:
			# 	print("EXCEPTION LazyJitsiUserStatusEncoder", e)
			# 	Jitsi_Websocket_Error.objects.create(file="jitsi_database_asynce.py",
			# 			function_name="disconnect_set_room_and_jitsi_status",
			# 			location_in_function="LazyJitsiUserStatusEncoder",
			# 			occurred_for_user=str(user.username),
			# 			error_text=str(e))

			try:
				s2 = LazyJitsiRoomAndParticipantsEncoder()
				payload['jitsi_room_data'] = s2.serialize([j_room])
			except Exception as e:
				print("EXCEPTION LazyJitsiRoomAndParticipantsEncoder", e)
				Jitsi_Websocket_Error.objects.create(file="jitsi_database_asynce.py",
						function_name="disconnect_set_room_and_jitsi_status",
						location_in_function="LazyJitsiRoomAndParticipantsEncoder",
						occurred_for_user=str(user.username),
						error_text=str(e))			
			
			data = json.dumps(payload)
			

		else:
			send_data = False
			payload={}
			data = json.dumps(payload)

	except Exception as e:
		print("EXCEPTION disconnect_set_room_and_jitsi_status", e)
		Jitsi_Websocket_Error.objects.create(file="jitsi_database_async.py",
						function_name="disconnect_set_room_and_jitsi_status",
						location_in_function="overall try",
						occurred_for_user=str(user.username),
						error_text=str(e))

	return send_data, data

@database_sync_to_async
def reset_room(sender_id, room_id):
	try:
		room = Room.objects.get(id=room_id)
		sending= CustomUser.objects.get(id = sender_id)
		j_room, created = Jitsi_Meeting_Room.objects.get_or_create(room = room)
		print("API J_Room", j_room)
		j_room.occupied = False
		j_room.mismatch = False
		j_room.count = 0
		j_room.student_alone = False
		j_room.participants.clear()
		j_room.save()
	except Exception as e:
		print("*****EXCEPTION reset_room", e)
		Jitsi_Websocket_Error.objects.create(file="jitsi_database_async.py",
						function_name="reset_room",
						location_in_function="overall try",
						occurred_for_user=str(sending.username),
						error_text=str(e))


@database_sync_to_async
def api_set_room_participants(sender_id, room_id, room_participants):
	print("Parameters", room_id, room_participants)
	
	data ="This"
	try:
		print("\n\napi_set_room_participants", type(room_participants))
		room = Room.objects.get(id=room_id)
		sending= CustomUser.objects.get(id = sender_id)

		print("Room", room)

		try:
			j_room, created = Jitsi_Meeting_Room.objects.get_or_create(room = room)
			print("API J_Room", j_room)
			
			for p in room_participants:
				print(p)
				the_user = CustomUser.objects.get(username=p.displayName)
				j_room.add_participant(the_user)
				j_room.check_student_alone_mismatch()
		except Exception as e:
			print("*****EXCEPTION API J_Room", e)
			
		
		# try:
		# 	for item in participants:
		# 		print(item['displayName'])
		# 		user = CustomUser.objects.get(username=item['displayName'])
		# 		jitsi_status, created = Jitsi_User_Status.objects.get_or_create(user=user)
		# 		jitsi_status.online = True
		# 		if joining:
		# 			jitsi_status.room = room
		# 		jitsi_status.jitsi_id =item['participantId']
		# 		jitsi_status.save()
		# 		j_room.add_participant(user)
		# except Exception as e:
		# 	print("*****EXCEPTION add_participant", e)


		# try:
		# 	j_room.check_student_alone_mismatch()
		# except Exception as e:
		# 	print("*****EXCEPTION check_student_alone_mismatch", e)
	

		

		# # j_room_data = Jitsi_Meeting_Room_Serializer(instance=j_room).data
		# # print("Data in db file", j_room_data, type(j_room_data))

		# # json_room = serialize('json', [j_room], cls=Lazy_Jitsi_Meeting_Room_Serializer)
		# # print("json_room in db file", json_room, type(json_room))
		try:
			payload={}
			s = LazyJitsiRoomAndParticipantsEncoder()
			payload['jitsi_room_data'] = s.serialize([j_room])
			data = json.dumps(payload)
			print("\n\napi_set_room_participants Data in db", data)
		except Exception as e:
			print("*****EXCEPTION serialize", e)
		
		

	except Exception as e:
		print("*****EXCEPTION set_room_participants", e)

	return data

# @database_sync_to_async
# def db_set_room_participants(jitsi_room, participants, joining, sender_id):
# 	print("Parameters", jitsi_room, participants)
# 	print(joining, sender_id)
# 	data ="This"
# 	try:
# 		print("\n\nset_room_participants", jitsi_room, participants, type(participants))
# 		room = Room.objects.get(name=jitsi_room)
# 		sending= CustomUser.objects.get(id = sender_id)

# 		print("Room", room)

# 		try:
# 			j_room, created = Jitsi_Meeting_Room.objects.get_or_create(room = room)
# 			print("J_Room", j_room)
# 			for p in j_room.participants.all():
# 				if sending == p and not joining:
# 					j_status, created = Jitsi_User_Status.objects.get_or_create(user=p)
# 					j_status.online= False
# 					j_status.jitsi_id = None
# 					j_status.room = None
# 					j_status.save()
# 					j_room.remove_participant(p)
# 		except Exception as e:
# 			print("*****EXCEPTION remove_participant", e)
			
		
# 		try:
# 			for item in participants:
# 				print(item['displayName'])
# 				user = CustomUser.objects.get(username=item['displayName'])
# 				jitsi_status, created = Jitsi_User_Status.objects.get_or_create(user=user)
# 				jitsi_status.online = True
# 				if joining:
# 					jitsi_status.room = room
# 				jitsi_status.jitsi_id =item['participantId']
# 				jitsi_status.save()
# 				j_room.add_participant(user)
# 		except Exception as e:
# 			print("*****EXCEPTION add_participant", e)


# 		try:
# 			j_room.check_student_alone_mismatch()
# 		except Exception as e:
# 			print("*****EXCEPTION check_student_alone_mismatch", e)
	

		

# 		# j_room_data = Jitsi_Meeting_Room_Serializer(instance=j_room).data
# 		# print("Data in db file", j_room_data, type(j_room_data))

# 		# json_room = serialize('json', [j_room], cls=Lazy_Jitsi_Meeting_Room_Serializer)
# 		# print("json_room in db file", json_room, type(json_room))
# 		try:
# 			payload={}
# 			s = LazyJitsiRoomAndParticipantsEncoder()
# 			payload['jitsi_room_data'] = s.serialize([j_room])
# 			data = json.dumps(payload)
# 			print("Data in db", data)
# 		except Exception as e:
# 			print("*****EXCEPTION serialize", e)
		
		

# 	except Exception as e:
# 		print("*****EXCEPTION set_room_participants", e)

# 	return data