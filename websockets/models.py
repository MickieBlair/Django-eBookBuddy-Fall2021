from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save, pre_delete
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from users.models import CustomUser
from site_admin.models import Room
# from reading_sessions.models import Scheduled_Match_Status
from site_admin.models import Daily_Session


# Create your models here.

class Redirect(models.Model):
	user_to_redirect = models.OneToOneField(CustomUser,
							related_name='redirect',
							on_delete=models.CASCADE , unique=True)

	to_room = models.ForeignKey(Room, on_delete=models.CASCADE, 
							related_name='location', null=True, blank=True)

	to_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, 
							related_name='redirect_to', null=True, blank=True)

	redirect_url = models.URLField(max_length=500, null=True, unique=False,
								 blank=True)
	auto_send = models.BooleanField(default=False)

	created_by = models.ForeignKey(CustomUser, related_name='created_by_user',
									on_delete=models.CASCADE, null=True, blank=True)

	def __str__(self):
		return self.user_to_redirect.username

	class Meta:
		verbose_name = 'Redirect'
		verbose_name_plural = 'Redirects'


def pre_save_redirect_receiver(sender, instance, *args, **kwargs):
	instance.user_to_redirect.status_ws.has_ws_redirect = True
	instance.user_to_redirect.status_ws.save()
	if instance.to_room:
		instance.redirect_url = settings.BASE_URL + "/sessions/room/" + instance.to_room.slug +"/"

pre_save.connect(pre_save_redirect_receiver, sender=Redirect)

def pre_delete_redirect_receiver(sender, instance, *args, **kwargs):
	print("Redirect Being Delete")
	instance.user_to_redirect.status_ws.has_redirect = False
	instance.user_to_redirect.status_ws.save()

pre_delete.connect(pre_delete_redirect_receiver, sender=Redirect)



class Websocket_Error(models.Model):
	file = models.CharField(max_length=255, null=True, blank=True)
	function_name = models.CharField(max_length=255, null=True, blank=True)
	location_in_function = models.CharField(max_length=255, null=True, blank=True)		
	occurred_for_user = models.CharField(max_length=255, null=True, blank=True)
	error_text = models.TextField(max_length=2000, null=True, blank=True)
	created	= models.DateTimeField(verbose_name='created', auto_now_add=True)

	class Meta:
		ordering = ['-created']
		verbose_name = 'Websocket Error'
		verbose_name_plural = 'Websocket Errors'

	def __str__(self):
		return self.file

class Staff_Chat_Error(models.Model):
	file = models.CharField(max_length=255, null=True, blank=True)
	function_name = models.CharField(max_length=255, null=True, blank=True)
	location_in_function = models.CharField(max_length=255, null=True, blank=True)		
	occurred_for_user = models.CharField(max_length=255, null=True, blank=True)
	error_text = models.TextField(max_length=2000, null=True, blank=True)
	created	= models.DateTimeField(verbose_name='created', auto_now_add=True)

	class Meta:
		ordering = ['-created']
		verbose_name = 'Staff Chat Error'
		verbose_name_plural = 'Staff Chat Errors'

	def __str__(self):
		return self.file

class Room_Chat_Error(models.Model):
	file = models.CharField(max_length=255, null=True, blank=True)
	function_name = models.CharField(max_length=255, null=True, blank=True)
	location_in_function = models.CharField(max_length=255, null=True, blank=True)		
	occurred_for_user = models.CharField(max_length=255, null=True, blank=True)
	error_text = models.TextField(max_length=2000, null=True, blank=True)
	created	= models.DateTimeField(verbose_name='created', auto_now_add=True)

	class Meta:
		ordering = ['-created']
		verbose_name = 'Room Chat Error'
		verbose_name_plural = 'Room Chat Errors'

	def __str__(self):
		return self.file

class Socket_Group(models.Model):
	name = models.CharField(max_length=255, null=False, blank=False, unique=True)
	count = models.IntegerField(verbose_name="Count", default=0)
	connected_users = models.ManyToManyField(CustomUser, related_name="group_connected", blank=True,)
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")

	def in_group(self):
		return self.connected_users.all()

	def add_user(self, user):
		self.connected_users.add(user)
		self.count = self.connected_users.all().count()
		self.save()
		return self.connected_users.all()

	def remove_user(self,user):
		self.connected_users.remove(user)
		self.count = self.connected_users.all().count()
		self.save()
		return self.connected_users.all()

	class Meta:
		verbose_name = 'Socket Group'
		verbose_name_plural = 'Socket Groups'

	def __str__(self):
		return self.name



class Notification(models.Model):

	# Who the notification is sent to
	target = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

	# The user that the creation of the notification was triggered by.
	from_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True,
								related_name="from_user")

	redirect_url = models.URLField(max_length=500, null=True, unique=False, blank=True, help_text="The URL to be visited when a notification is clicked.")

	# statement describing the notification (ex: "Mitch sent you a friend request")
	verb = models.CharField(max_length=255, unique=False, blank=True, null=True)

	# When the notification was created/updated
	timestamp = models.DateTimeField(auto_now_add=True)

	# Some notifications can be marked as "read". (I used "read" instead of "active". I think its more appropriate)
	read = models.BooleanField(default=False)

	# A generic type that can refer to a FriendRequest, Unread Message, or any other type of "Notification"
	# See article: https://simpleisbetterthancomplex.com/tutorial/2016/10/13/how-to-use-generic-relations.html
	content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
	object_id = models.PositiveIntegerField()
	content_object = GenericForeignKey()

	def __str__(self):
		return self.verb

	class Meta:
		verbose_name = 'Notification'
		verbose_name_plural = 'Notifications'

	def get_content_object_type(self):
		# if self.content_object:
		return str(self.content_object.get_cname)
		# else:
		# 	self.content_object = GenericForeignKey()
		# 	self.save()
		# 	return str(self.content_object.get_cname)

def pre_save_notification_receiver(sender, instance, *args, **kwargs):
	# print("TARGET", instance.target)
	pass

pre_save.connect(pre_save_notification_receiver, sender=Notification)




class Jitsi_Chat_Room(models.Model):
	# Room title
	title = models.CharField(max_length=255, unique=True, blank=False,)
	slug = models.SlugField(max_length=100, null=True, blank=True, unique=True)
	date_created = models.DateField(auto_now_add=True, verbose_name="date created")

	# all users who are authenticated and viewing the chat
	users = models.ManyToManyField(CustomUser,
									blank=True,)

	def __str__(self):
		return self.title


	def connect_user(self, user):
		"""
		return true if user is added to the users list
		"""
		jitsi_room = user.session_status.room
		is_user_added = False
		if not user in self.users.all():
			self.users.add(user)
			self.save()
			is_user_added = True
		elif user in self.users.all():
			is_user_added = True
		return is_user_added, jitsi_room 


	def disconnect_user(self, user, jitsi_room):
		print("\n\n\n\n\nDISCONNECT USER MODEL Jitsi_Chat_Room")
		"""
		return true if user is removed from the users list
		"""
		# print("\n\n\n***** Disconnecting from Room", user)

		is_user_removed = False
		if user in self.users.all():
			self.users.remove(user)
			self.save()
			is_user_removed = True

			if jitsi_room.participants.all().count() == 0:
				print("\n\n\nNO USERS REMAINING IN ROOM")
				messages = Jitsi_Room_Chat_Message.objects.filter(meeting_room=jitsi_room, display=True)
				for message in messages:
					message.display = False
					message.save()
			else:
				print("room occupied")

		room_message_count = Jitsi_Room_Unread_Chat_Message.objects.get(user=user)
		room_message_count.unread_count = 0
		room_message_count.room = None   
		room_message_count.save()

		return is_user_removed 

	class Meta:
		verbose_name = 'Jitsi Chat Room'
		verbose_name_plural = 'Jitsi Chat Rooms'

	@property
	def group_name(self):
		"""
		Returns the Channels Group name that sockets should subscribe to to get sent
		messages as they are generated.
		"""
		return "Jitsi_Chat_Room-%s" % self.id


class Jitsi_Chat_Room_Message_Manager(models.Manager):

	def by_jitsi_room(self, jitsi_room):
		qs = Jitsi_Room_Chat_Message.objects.filter(meeting_room=jitsi_room,
											 display=True).order_by("-timestamp")
		return qs

	def by_room(self, room, jitsi_room_id):
		jitsi_room = Room.objects.get(id=jitsi_room_id)
		qs = Jitsi_Room_Chat_Message.objects.filter(room=room,
											 meeting_room=jitsi_room,
											 display=True).order_by("-timestamp")
		return qs

class Jitsi_Room_Chat_Message(models.Model):
	"""
	Chat message created by a user inside a PublicChatRoom
	"""
	user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
	room = models.ForeignKey(Jitsi_Chat_Room, on_delete=models.CASCADE)
	meeting_room = models.ForeignKey(Room, on_delete=models.CASCADE, 
							related_name='jitsi_room_messages', null=True, blank=True)
	timestamp = models.DateTimeField(auto_now_add=True)
	content = models.TextField(unique=False, blank=False,)
	display = models.BooleanField(default=True)

	objects = Jitsi_Chat_Room_Message_Manager()

	def __str__(self):
		return self.content


	class Meta:
		verbose_name = 'Jitsi Chat Room Message'
		verbose_name_plural = 'Jitsi Chat Room Messages'


class Jitsi_Room_Unread_Chat_Message(models.Model):
	user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="unread_user")
	room = models.ForeignKey(Jitsi_Room_Chat_Message, on_delete=models.CASCADE,
												 null=True, blank=True,
												 related_name="room_unread_general")
	meeting_room = models.ForeignKey(Room, on_delete=models.CASCADE, 
							related_name='jitsi_messages', null=True, blank=True)
	unread_count = models.IntegerField(verbose_name="Unread Count", default=0)
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")

	def __str__(self):
		return self.user.username + " Unread Count"

	def add_one(self, jitsi_room):
		self.unread_count = self.unread_count + 1
		self.meeting_room = jitsi_room
		self.save()

	def reset_count(self): 
		self.unread_count = 0
		self.save()

	class Meta:
		verbose_name = 'Jitsi Chat Uread Message'
		verbose_name_plural = 'Jitsi Chat Unread Messages'


class Staff_Chat_Room(models.Model):
	# Room title
	title = models.CharField(max_length=255, unique=True, blank=False,)
	slug = models.SlugField(max_length=100, null=True, blank=True, unique=True)
	date_created = models.DateField(auto_now_add=True, verbose_name="date created")

	# all users who are authenticated and viewing the chat
	users = models.ManyToManyField(CustomUser,
									blank=True,)

	def __str__(self):
		return self.title


	def connect_user(self, user):
		"""
		return true if user is added to the users list
		"""
		print("Connecting User in Models.PY")
		is_user_added = False
		try:
			if not user in self.users.all():
				self.users.add(user)
				self.save()
				is_user_added = True
			elif user in self.users.all():
				is_user_added = True
		except Exception as e:
			Staff_Chat_Error.objects.create(file="websockets Staff Chat models.py ",
						function_name=socket_info['connect_user(self, user)'],
						location_in_function=socket_info['connect user'],
						occurred_for_user=user.username,
						error_text=str(e))		
		return is_user_added 


	def disconnect_user(self, user):
		"""
		return true if user is removed from the users list
		"""
		is_user_removed = False
		try:
			if user in self.users.all():
				self.users.remove(user)
				self.save()
				is_user_removed = True
		except Exception as e:
			Staff_Chat_Error.objects.create(file="websockets Staff Chat models.py ",
						function_name=socket_info['disconnect_user(self, user)'],
						location_in_function=socket_info['disconnect user'],
						occurred_for_user=user.username,
						error_text=str(e))	
		
		
		return is_user_removed 

	class Meta:
		verbose_name = 'Staff Chat Room'
		verbose_name_plural = 'Staff Chat Rooms'


	@property
	def group_name(self):
		"""
		Returns the Channels Group name that sockets should subscribe to to get sent
		messages as they are generated.
		"""
		return "Staff_Chat_Room-%s" % self.id

def post_save_create_staff_unread_receiver(sender, instance, *args, **kwargs):
	all_staff = CustomUser.objects.filter(role__name="Staff")
	for member in all_staff:
		staff_unread, created = Staff_Room_Unread_Chat_Message.objects.get_or_create(user=member)
		if created:
			staff_unread.room = instance 
			staff_unread.unread_count = 0  
			staff_unread.save()

post_save.connect(post_save_create_staff_unread_receiver, sender=Staff_Chat_Room)

class Staff_Chat_Room_Message_Manager(models.Manager):
	def by_room(self, room):
		qs = Staff_Room_Chat_Message.objects.filter(room=room).order_by("-timestamp")
		return qs

class Staff_Room_Chat_Message(models.Model):
	user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
	room = models.ForeignKey(Staff_Chat_Room, on_delete=models.CASCADE,)
	meeting_room = models.ForeignKey(Room, on_delete=models.CASCADE, 
							related_name='staff_messages', null=True, blank=True)
	timestamp = models.DateTimeField(auto_now_add=True)
	content = models.TextField(unique=False, blank=False,)

	objects = Staff_Chat_Room_Message_Manager()

	def __str__(self):
		return self.content

	class Meta:
		verbose_name = 'Staff Chat Room Message'
		verbose_name_plural = 'Staff Chat Room Messages'



class Staff_Room_Unread_Chat_Message(models.Model):
	user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="unread_staff")
	room = models.ForeignKey(Staff_Chat_Room, on_delete=models.CASCADE,
												 null=True, blank=True,
												 related_name="room_unread_staff")
	unread_count = models.IntegerField(verbose_name="Unread Count", default=0)
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")

	def __str__(self):
		return self.user.username + " Unread Count"

	def add_one(self):
		self.unread_count = self.unread_count + 1
		self.save()

	def reset_count(self): 
		self.unread_count = 0
		self.save()

	class Meta:
		verbose_name = 'Staff Chat Uread Message'
		verbose_name_plural = 'Staff Chat Unread Messages'


class Help_Request(models.Model):
	from_user = models.ForeignKey(CustomUser,
							related_name='request',
							on_delete=models.CASCADE, unique=False)
	from_room = models.ForeignKey(Room, on_delete=models.CASCADE, 
							related_name='room_needing_help', null=True, blank=True, unique=False)
	room_url = models.URLField(max_length=500, null=True, unique=False,
								 blank=True)
	created = models.DateTimeField(auto_now_add=True)
	message = models.TextField(unique=False, blank=False,)
	user_message = models.TextField(unique=False, blank=True,)
	done = models.BooleanField(default=False)
	visited_by = models.ForeignKey(CustomUser,
							related_name='completed_by', null=True, blank=True,
							on_delete=models.CASCADE, unique=False)
	visited_time = models.DateTimeField(verbose_name="visited time", null=True, blank=True,)

	def mark_as_done(self, completed_by):
		print("IN MARK AS DONE", completed_by)
		user = CustomUser.objects.get(id = completed_by)
		print(user)
		self.visited_by = user
		self.done = True
		self.visited_time = timezone.now()
		self.save()

	def __str__(self):
		return self.from_user.username

	class Meta:
		verbose_name = 'Help Request'
		verbose_name_plural = 'Help Requests'



def pre_save_help_request_receiver(sender, instance, *args, **kwargs):
	if not instance.room_url:
		instance.room_url = settings.BASE_URL + "/sessions/" + instance.from_room.slug +"/"

pre_save.connect(pre_save_help_request_receiver, sender=Help_Request)


class Private_Message_Manager(models.Manager):

	def by_conversation_read(self, to_user, from_user):
		qs = Private_Message.objects.filter(from_user=from_user, to_user=to_user,
											message_read=True).order_by("-date_created")
		return qs

	def by_conversation_unread(self, to_user, from_user):
		qs = Private_Message.objects.filter(from_user=from_user, to_user=to_user,
											message_read=False).order_by("-date_created")
		return qs

	def conversations_all(self, to_user):
		# conversations = "This"
		conversations = Private_Message.objects.filter(to_user=to_user).order_by().values_list('from_user').distinct()

		print(conversations)


		# qs = Private_Message.objects.filter(from_user=from_user,
		# 									to_user=to_user).order_by("-date_created")
		return conversations

	def by_from_user_all(self, from_user):
		qs = Private_Message.objects.filter(from_user=from_user).order_by("-date_created")
		return qs

	def by_to_user_all(self, to_user):
		qs = Private_Message.objects.filter(to_user=to_user).order_by("-date_created")
		return qs

	def by_from_user_not_read(self, from_user):
		qs = Private_Message.objects.filter(from_user=from_user, message_read=False).order_by("-date_created")
		return qs

	def by_to_user_not_read(self, to_user):
		qs = Private_Message.objects.filter(to_user=to_user, message_read=False).order_by("-date_created")
		return qs

	def by_from_user_read(self, from_user):
		qs = Private_Message.objects.filter(from_user=from_user, message_read=True).order_by("-date_created")
		return qs

	def by_to_user_read(self, to_user):
		qs = Private_Message.objects.filter(to_user=to_user, message_read=True).order_by("-date_created")
		return qs




class Private_Message(models.Model):
	"""
	Chat message created by a user inside a Room
	"""
	from_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="sender")
	to_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="recipient")
	message_read = models.BooleanField(default=False)
	read_at = models.DateTimeField(null=True, blank=True, verbose_name="read at")
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	message = models.TextField(unique=False, blank=False,)

	objects = Private_Message_Manager()

	def __str__(self):
		return self.from_user.username + " to " + self.to_user.username

	class Meta:
		verbose_name = 'Private Message'
		verbose_name_plural = 'Private Messages'

def post_save_private_receiver(sender, instance, *args, **kwargs):
	print('Private post_save')

	if Private_Conversation_Pair.objects.filter(user1=instance.from_user,
												 user2=instance.to_user).exists():
		# print("1 Exists")
		pair, created = Private_Conversation_Pair.objects.get_or_create(user1=instance.from_user,
															 user2=instance.to_user)

	elif Private_Conversation_Pair.objects.filter(user1=instance.to_user,
												 user2=instance.from_user).exists():
		# print("2 Exists")
		pair, created = Private_Conversation_Pair.objects.get_or_create(user1=instance.to_user,
												 user2=instance.from_user)
	else:
		pair, created = Private_Conversation_Pair.objects.get_or_create(user1=instance.from_user,
															 user2=instance.to_user)


	pair.add_message(instance)
	

	user1_has_unread = False  
	user2_has_unread =False  

	for message in pair.messages.all():
		if message.to_user == pair.user1:
			# print("This message was sent to user1 ", instance.user1)
			# print("message read", message.message_read)
			if not message.message_read:
				user1_has_unread = True

		elif message.to_user == pair.user2:
			# print("This message was sent to user2 ", instance.user2)
			# print("message read", message.message_read)
			if not message.message_read:
				user2_has_unread = True
				
	pair.user1_has_unread = user1_has_unread
	pair.user2_has_unread = user2_has_unread		
	pair.save()



post_save.connect(post_save_private_receiver, sender=Private_Message)

class Private_Conversation_Pair(models.Model):
	user1 = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="user_1")	
	user2 = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="user_2")
	users = models.ManyToManyField(CustomUser, related_name="pair_users", blank=True,)
	messages = models.ManyToManyField(Private_Message, related_name="pair_messages", blank=True,)
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")
	user1_has_unread = models.BooleanField(default=True)
	user2_has_unread = models.BooleanField(default=True)

	def __str__(self):
		return self.user1.username + " - " + self.user2.username

	def add_message(self, message):
		self.messages.add(message)

	class Meta:
		verbose_name = 'Private Conversation Pair'
		verbose_name_plural = 'Private Conversation Pairs'

def post_save_conversation_receiver(sender, instance, *args, **kwargs):
	if instance.user1 not in instance.messages.all():
		instance.users.add(instance.user1)

	if instance.user2 not in instance.messages.all():
		instance.users.add(instance.user2)

	

	


post_save.connect(post_save_conversation_receiver, sender=Private_Conversation_Pair)

# class Conversation(models.Model):
	
# 	message_count = models.IntegerField(default=0)
# 	unread_count = models.IntegerField(default=0)
# 	messages = models.ManyToManyField(Private_Message, related_name="conversation_messages", blank=True,)
	

# 	def __str__(self):
# 		return self.from_user.username + " - " + self.to_user.username

# 	def add_message(self, message):
# 		self.messages.add(message)

# 	def remove_message(self, message):
# 		self.messages.remove(message)

# 	class Meta:
# 		verbose_name = 'Conversation'
# 		verbose_name_plural = 'Conversations'









class PrivateChatRoom(models.Model):
	"""
	A private room for people to chat in.
	"""
	user1 = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="user1")
	user2 = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="user2")

	# Users who are currently connected to the socket (Used to keep track of unread messages)
	connected_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="connected_users")
	members =  models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="room_members")
	is_active = models.BooleanField(default=False)
	last_use = models.DateTimeField(blank=False, null=False)

	def connect_user(self, user):
		"""
		return true if user is added to the connected_users list
		"""
		self.last_use = timezone.now()
		self.save()
		is_user_added = False
		if not user in self.connected_users.all():
			self.connected_users.add(user)
			is_user_added = True
		return is_user_added 


	def disconnect_user(self, user):
		"""
		return true if user is removed from connected_users list
		"""
		is_user_removed = False
		if user in self.connected_users.all():
			self.connected_users.remove(user)
			is_user_removed = True
		return is_user_removed

	def unread_count_by_user(self, user):
		# print("*******unread_count_by_user", self, user)
		user_unread = UnreadChatRoomMessages.objects.get(user=user, room=self)
		# print(user_unread.count)
		return user_unread.count

	def total_message_count(self):
		# print("*******unread_count_by_user", self, user)
		total = RoomChatMessage.objects.by_room(self).count()
		# print(user_unread.count)
		return total

	def __str__(self):
		return self.user1.username + " - " + self.user2.username

	class Meta:
		verbose_name = 'Private Chat Room'
		verbose_name_plural = 'Private Chat Rooms'

	@property
	def group_name(self):
		"""
		Returns the Channels Group name that sockets should subscribe to to get sent
		messages as they are generated.
		"""
		return f"PrivateChatRoom-{self.id}"

def post_save_private_room_receiver(sender, instance, created, **kwargs):
	if created:
		print("*************CREATED")
		instance.members.add(instance.user1)
		instance.members.add(instance.user2)




post_save.connect(post_save_private_room_receiver, sender=PrivateChatRoom)


class RoomChatMessageManager(models.Manager):
	def by_room(self, room):
		qs = RoomChatMessage.objects.filter(room=room).order_by("-timestamp")
		return qs

class RoomChatMessage(models.Model):
	"""
	Chat message created by a user inside a Room

	"""
	from_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="msg_sender")
	to_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="msg_recipient")
	user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
	room = models.ForeignKey(PrivateChatRoom, on_delete=models.CASCADE)
	timestamp = models.DateTimeField(auto_now_add=True)
	content = models.TextField(unique=False, blank=False,)

	objects = RoomChatMessageManager()

	def __str__(self):
		return "From: " + self.from_user.username + " To: " + self.to_user.username

	class Meta:
		verbose_name = 'Private Chat Room Message'
		verbose_name_plural = 'Private Chat Room Messages'



class UnreadChatRoomMessages(models.Model):
	"""
	Keep track of the number of unread messages by a specific user in a specific private chat.
	When the user connects the chat room, the messages will be considered "read" and 'count' will be set to 0.
	"""
	room = models.ForeignKey(PrivateChatRoom, on_delete=models.CASCADE, related_name="room_unread")

	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="private_unread")

	count = models.IntegerField(default=0)

	most_recent_message = models.CharField(max_length=500, blank=True, null=True)	

	# last time msgs were read by the user
	reset_timestamp     = models.DateTimeField()

	notifications       = GenericRelation(Notification)

	last_message = models.ForeignKey(RoomChatMessage, on_delete=models.CASCADE,
									 related_name="last", null=True, blank=True)
	unread_msgs = models.ManyToManyField(RoomChatMessage, related_name="unread_messages", blank=True,)



	def __str__(self):
		return f"Messages that {str(self.user.username)} has not read yet."

	def get_unread_in_room_count(user, room):
		unread_count = UnreadChatRoomMessages.objects.get(room=room, user=user)
		return unread_count.count


	def save(self, *args, **kwargs):
		if not self.id: # if just created, add a timestamp. Otherwise do not automatically change it ever.
			self.reset_timestamp = timezone.now()
		return super(UnreadChatRoomMessages, self).save(*args, **kwargs)

	class Meta:
		verbose_name = 'Unread Private Chat Message'
		verbose_name_plural = 'Unread Private Chat Messages'

	@property
	def get_cname(self):
		"""
		For determining what kind of object is associated with a Notification
		"""
		return "UnreadChatRoomMessages"

	@property
	def get_other_user(self):
		"""
		Get the other user in the chat room
		"""
		if self.user == self.room.user1:
			return self.room.user2
		else:
			return self.room.user1


@receiver(post_save, sender=PrivateChatRoom)
def create_unread_chatroom_messages_obj(sender, instance, created, **kwargs):
	if created:
		unread_msgs1 = UnreadChatRoomMessages(room=instance, user=instance.user1)
		unread_msgs1.save()

		unread_msgs2 = UnreadChatRoomMessages(room=instance, user=instance.user2)
		unread_msgs2.save()



@receiver(pre_save, sender=UnreadChatRoomMessages)
def increment_unread_msg_count(sender, instance, **kwargs):
	"""
	When the unread message count increases, update the notification. 
	If one does not exist, create one. (This should never happen)
	"""
	if instance.id is None: # new object will be created
		pass # create_unread_chatroom_messages_obj will handle this scenario
	else:
		previous = UnreadChatRoomMessages.objects.get(id=instance.id)
		if previous.count < instance.count: # if count is incremented
			content_type = ContentType.objects.get_for_model(instance)
			if instance.user == instance.room.user1:
				other_user = instance.room.user2
			else:
				other_user = instance.room.user1
			try:
				notification = Notification.objects.get(target=instance.user, content_type=content_type, object_id=instance.id)
				# notification.verb = instance.most_recent_message
				notification.verb = "New Message from " + other_user.full_name
				notification.timestamp = timezone.now()
				notification.save()
			except Notification.DoesNotExist:
				instance.notifications.create(
					target=instance.user,
					from_user=other_user,
					redirect_url=f"{settings.BASE_URL}/chat/?room_id={instance.room.id}", # we want to go to the chatroom
					verb="New Message from " + other_user.full_name,
					content_type=content_type,
				)


@receiver(pre_save, sender=UnreadChatRoomMessages)
def remove_unread_msg_count_notification(sender, instance, **kwargs):
	"""
	If the unread messge count decreases, it means the user joined the chat. So delete the notification.
	"""
	if instance.id is None: # new object will be created
		pass # create_unread_chatroom_messages_obj will handle this scenario
	else:
		previous = UnreadChatRoomMessages.objects.get(id=instance.id)
		if previous.count > instance.count: # if count is decremented
			content_type = ContentType.objects.get_for_model(instance)
			try:
				notification = Notification.objects.get(target=instance.user, content_type=content_type, object_id=instance.id)
				notification.delete()
			except Notification.DoesNotExist:
				pass
				# Do nothing


class User_Private_Room_List(models.Model):
	user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="private_room_list")
	private_rooms =  models.ManyToManyField(PrivateChatRoom, blank=True, related_name="private_room_list_rooms")
	room_count = models.IntegerField(default=0)
	total_unread_private = models.IntegerField(default=0)
	date_created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
	last_updated = models.DateTimeField(auto_now=True, verbose_name="last updated")

	def __str__(self):
		return self.user.username + " Private Room List"

	def add_room(self, room):
		self.private_rooms.add(room)
		self.room_count = self.private_rooms.all().count()
		self.save()

	def remove_room(self, room):
		self.private_rooms.remove(room)
		self.room_count = self.private_rooms.all().count()
		self.save()

	def total_all_unread(self):
		try:
			total = 0
			for pvt in self.private_rooms.all():
				u_read = UnreadChatRoomMessages.objects.get(user=self.user, room=pvt)
				total = total + u_read.count

			self.total_unread_private = total  
			self.save()
		except Exception as e:
			print("Broken Model", e)
		


	class Meta:
		verbose_name = 'User Private Room List'
		verbose_name_plural = 'User Private Room List'













# class Scheduled_Match_Status_NotificationList(models.Model):

# 	user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="notification_list")

# 	# set up the reverse relation to GenericForeignKey

# 	notifications = GenericRelation(Notification)

# 	def __str__(self):
# 		return self.user.username

# 	class Meta:
# 		verbose_name = 'Scheduled Match Status Notification List'
# 		verbose_name_plural = 'Scheduled Match Status Notification Lists'

# 	def add_match_status_notification(self, target, from_user, verb):
# 		content_type = ContentType.objects.get_for_model(Scheduled_Match_Status)

# 		# staff_notification = Notification.objects.create(target=target,
# 				# 											from_user = from_user,
# 				# 											verb = verb,
# 				# 											content_type = content_type,
# 				# 											object_id = redirect.id)
# 				# staff_notification.save()

# 		self.notifications.create(
# 				target=target,
# 				from_user=from_user,
# 				verb=verb,
# 				content_type=content_type,
# 			)
# 		self.save()


# 	@property
# 	def get_cname(self):
# 		"""
# 		For determining what kind of object is associated with a Notification
# 		"""
# 		return "Scheduled_Match_Status_NotificationList"


# class User_Redirect_Notification(models.Model):

# 	user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="redirect_notification")

# 	notifications = GenericRelation(Notification)

# 	def __str__(self):
# 		return self.user.username + "Redirects"

# 	class Meta:
# 		verbose_name = 'User Redirect Notification'
# 		verbose_name_plural = 'User Redirect Notifications'

# 	def add_redirect_notification(self, target, from_user, verb):
# 		print("\n\n\nADD REDIRECT", target, from_user, verb)
# 		content_type = ContentType.objects.get_for_model(Redirect)

# 		self.notifications.create(
# 				target=target,
# 				from_user=from_user,
# 				verb=verb,
# 				content_type=content_type,
# 			)
# 		self.save()


# 	@property
# 	def get_cname(self):
# 		"""
# 		For determining what kind of object is associated with a Notification
# 		"""
# 		return "User_Redirect_Notification"


				# # Create a private chat (or activate an old one)
			# chat = find_or_create_private_chat(self.user, account)
			# if not chat.is_active:
			# 	chat.is_active = True
			# 	chat.save()

	# def remove_friend(self, account):
	# 	"""
	# 	Remove a friend.
	# 	"""
	# 	if account in self.friends.all():
	# 		self.friends.remove(account)

	# 		# Deactivate the private chat between these two users
	# 		chat = find_or_create_private_chat(self.user, account)
	# 		if chat.is_active:
	# 			chat.is_active = False
	# 			chat.save()

	# def unfriend(self, removee):
	# 	"""
	# 	Initiate the action of unfriending someone.
	# 	"""
	# 	remover_friends_list = self # person terminating the friendship

	# 	# Remove friend from remover friend list
	# 	remover_friends_list.remove_friend(removee)

	# 	# Remove friend from removee friend list
	# 	friends_list = FriendList.objects.get(user=removee)
	# 	friends_list.remove_friend(remover_friends_list.user)

	# 	content_type = ContentType.objects.get_for_model(self)

	# 	# Create notification for removee
	# 	friends_list.notifications.create(
	# 		target=removee,
	# 		from_user=self.user,
	# 		redirect_url=f"{settings.BASE_URL}/account/{self.user.pk}/",
	# 		verb=f"You are no longer friends with {self.user.username}.",
	# 		content_type=content_type,
	# 	)

	# 	# Create notification for remover
	# 	self.notifications.create(
	# 		target=self.user,
	# 		from_user=removee,
	# 		redirect_url=f"{settings.BASE_URL}/account/{removee.pk}/",
	# 		verb=f"You are no longer friends with {removee.username}.",
	# 		content_type=content_type,
	# 	)


	# def is_mutual_friend(self, friend):
	# 	"""
	# 	Is this a friend?
	# 	"""
	# 	if friend in self.friends.all():
	# 		return True
	# 	return False


