from datetime import datetime
from django.contrib.humanize.templatetags.humanize import naturalday
from django.core.serializers.python import Serializer
import pytz
from django.utils import timezone
from django.conf import settings
from pytz import timezone

from websockets.models import PrivateChatRoom, User_Private_Room_List, Websocket_Error
from websockets.private_chat_constants import *

def find_or_create_private_chat(user1, user2):
	try:
		if PrivateChatRoom.objects.filter(user1=user1, user2=user2).exists():
			chat = PrivateChatRoom.objects.get(user1=user1, 
													user2=user2)
		elif PrivateChatRoom.objects.filter(user1=user2, user2=user1).exists():
			chat = PrivateChatRoom.objects.get(user1=user2, 
													user2=user1)
		else:
			chat, created = PrivateChatRoom.objects.get_or_create(user1=user1,
																user2=user2,
																last_use=timezone.now())

		user1_list, created = User_Private_Room_List.objects.get_or_create(user=user1)
		print(user1_list)
		user1_list.add_room(chat)

		user2_list, created = User_Private_Room_List.objects.get_or_create(user=user2)
		print(user2_list)
		user2_list.add_room(chat)

	except Exception as e:
		print("BROKEN find_or_create_private_chat", e)
		Websocket_Error.objects.create(file="utils.py",
						function_name="find_or_create_private_chat",
						location_in_function="try block for find_or_create_private_chat",
						occurred_for_user=user1.username,
						error_text=e)

	return chat

def calculate_timestamp(timestamp):

	timestamp = timestamp.astimezone(timezone('US/Eastern'))
	ts = ""
	if (naturalday(timestamp) == "today") or (naturalday(timestamp) == "yesterday"):
		str_time = datetime.strftime(timestamp, "%I:%M %p")
		str_time = str_time.strip("0")
		ts = f"{naturalday(timestamp)} at {str_time}"
	# other days
	else:
		str_time = datetime.strftime(timestamp, "%m/%d/%Y")
		ts = f"{str_time}"
	return str(ts)

def calculate_date_time(timestamp):

	timestamp = timestamp.astimezone(timezone('US/Eastern'))
	return str(timestamp)















# from datetime import datetime
# from django.contrib.humanize.templatetags.humanize import naturalday
# from django.core.serializers.python import Serializer

# # from chat.models import PrivateChatRoom
# from websockets.staff_chat_constants import *
# import pytz
# from django.utils import timezone
# from django.conf import settings
# from pytz import timezone

# # def find_or_create_private_chat(user1, user2):
# # 	try:
# # 		chat = PrivateChatRoom.objects.get(user1=user1, user2=user2)
# # 	except PrivateChatRoom.DoesNotExist:
# # 		try:
# # 			chat = PrivateChatRoom.objects.get(user1=user2, user2=user1)
# # 		except PrivateChatRoom.DoesNotExist:
# # 			chat = PrivateChatRoom(user1=user1, user2=user2)
# # 			chat.save()
# # 	return chat


# def calculate_timestamp(timestamp):
# 	"""
# 	1. Today or yesterday:
# 		- EX: 'today at 10:56 AM'
# 		- EX: 'yesterday at 5:19 PM'
# 	2. other:
# 		- EX: 05/06/2020
# 		- EX: 12/28/2020
# 	"""
# 	ts = ""
# 	# Today or yesterday
# 	if (naturalday(timestamp) == "today") or (naturalday(timestamp) == "yesterday"):
# 		str_time = datetime.strftime(timestamp, "%I:%M %p")
# 		str_time = str_time.strip("0")
# 		ts = f"{naturalday(timestamp)} at {str_time}"
# 	# other days
# 	else:
# 		str_time = datetime.strftime(timestamp, "%m/%d/%Y")
# 		ts = f"{str_time}"
# 	return str(ts)


# def calculate_date_time(timestamp):

# 	timestamp = timestamp.astimezone(timezone('US/Eastern'))

# 	return str(timestamp)



# class LazyRoomChatMessageEncoder(Serializer):
#     def get_dump_object(self, obj):
#         dump_object = {}
#         dump_object.update({'msg_type': MSG_TYPE_MESSAGE})
#         dump_object.update({'msg_id': str(obj.id)})
#         dump_object.update({'user_id': str(obj.user.id)})
#         dump_object.update({'username': str(obj.user.username)})
#         dump_object.update({'message': str(obj.content)})
#         dump_object.update({'profile_image': str(obj.user.profile_image.url)})
#         dump_object.update({'natural_timestamp': calculate_timestamp(obj.timestamp)})
#         return dump_object


